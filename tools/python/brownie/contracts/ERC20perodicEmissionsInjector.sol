// SPDX-License-Identifier: MIT

pragma solidity 0.8.6;

import "@chainlink/contracts/src/v0.8/ConfirmedOwner.sol";
import "@chainlink/contracts/src/v0.8/interfaces/KeeperCompatibleInterface.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "interfaces/balancer/IChildChainStreamer.sol";


/**
 * @title The PeriodicRewardsInjector Contract
 * @author tritium.eth
 * @notice Modification of the Chainlink's EthBalanceMonitor to send ERC20s to a rewards distributor on a regular basis
 * @notice The contract includes the ability to withdraw eth and sweep all ERC20 tokens including the managed token to any address by the owner
 * see https://docs.chain.link/chainlink-automation/utility-contracts/
 */
contract periodicRewardsInjector is ConfirmedOwner, Pausable, KeeperCompatibleInterface {
    event gasTokenWithdrawn(uint256 amountWithdrawn, address recipient);
    event KeeperRegistryAddressUpdated(address oldAddress, address newAddress);
    event MinWaitPeriodUpdated(uint256 oldMinWaitPeriod, uint256 newMinWaitPeriod);
    event ERC20Swept(address indexed token, address recipient, uint256 amount);
    event injectionFailed(address gauge);
    event emissionsInjection(address gauge, uint256 amount);
    event forwardedCall(address targetContract);

    error InvalidStreamerList();
    error OnlyKeeperRegistry();
    error DuplicateAddress(address duplicate);
    error ZeroAddress();

    struct Target {
        bool isActive;
        uint256 amountPerPeriod;
        uint8 maxPeriods;
        uint8 periodNumber;
        uint56 lastInjectionTimeStamp; // enough space for 2 trillion years
    }

    address private s_keeperRegistryAddress;
    uint256 private s_minWaitPeriodSeconds;
    address[] private s_streamerList;
    mapping(address => Target) internal s_targets;
    address private s_injectTokenAddress;
    address public s_feeDistributorAddress;

     /**
   * @param keeperRegistryAddress The address of the keeper registry contract
   * @param minWaitPeriodSeconds The minimum wait period for address between funding (for security)
   * @param injectTokenAddress The ERC20 token this contract should mange
   */
    constructor(address keeperRegistryAddress, uint256 minWaitPeriodSeconds, address injectTokenAddress)
    ConfirmedOwner(msg.sender) {
        setKeeperRegistryAddress(keeperRegistryAddress);
        setMinWaitPeriodSeconds(minWaitPeriodSeconds);
        setInjectTokenAddress(injectTokenAddress);
    }

    /**
     * @notice Sets the list of addresses to watch and their funding parameters
   * @param streamerAddresses the list of addresses to watch
   * @param amountsPerPeriod the minimum balances for each address
   * @param maxPeriods the amount to top up each address
   */
    function setRecipientList(
        address[] calldata streamerAddresses,
        uint256[] calldata amountsPerPeriod,
        uint8[] calldata maxPeriods
    ) external onlyOwner {
        if (streamerAddresses.length != amountsPerPeriod.length || streamerAddresses.length != maxPeriods.length) {
            revert InvalidStreamerList();
        }
        address[] memory oldstreamerList = s_streamerList;
        for (uint256 idx = 0; idx < oldstreamerList.length; idx++) {
            s_targets[oldstreamerList[idx]].isActive = false;
        }
        for (uint256 idx = 0; idx < streamerAddresses.length; idx++) {
            if (s_targets[streamerAddresses[idx]].isActive) {
                revert DuplicateAddress(streamerAddresses[idx]);
            }
            if (streamerAddresses[idx] == address(0)) {
                revert InvalidStreamerList();
            }
            if (amountsPerPeriod[idx] == 0) {
                revert InvalidStreamerList();
            }
            s_targets[streamerAddresses[idx]] = Target({
            isActive : true,
            amountPerPeriod : amountsPerPeriod[idx],
            maxPeriods : maxPeriods[idx],
            lastInjectionTimeStamp : 0,
            periodNumber : 0
            });
        }
        s_streamerList = streamerAddresses;
    }

    /**
     * @notice Gets a list of addresses that are ready to inject
   * @return list of addresses that are ready to inject
   */
    function getReadyStreamers() public view returns (address[] memory) {
        address[] memory streamerlist = s_streamerList;
        address[] memory ready = new address[](streamerlist.length);
        address tokenaddress = s_injectTokenAddress;
        uint256 count = 0;
        uint256 minWaitPeriod = s_minWaitPeriodSeconds;
        uint256 balance = IERC20(tokenaddress).balanceOf(address(this));
        Target memory target;
        for (uint256 idx = 0; idx < streamerlist.length; idx++) {
            target = s_targets[streamerlist[idx]];
            IChildChainStreamer streamer = IChildChainStreamer(streamerlist[idx]);
            if (
                target.lastInjectionTimeStamp + minWaitPeriod <= block.timestamp &&
                streamer.reward_data(tokenaddress).period_finish >= block.timestamp &&
                balance >= target.amountPerPeriod &&
                target.periodNumber < target.maxPeriods
            ) {
                ready[count] = streamerlist[idx];
                count++;
                balance -= target.amountPerPeriod;
            }
        }
        if (count != streamerlist.length) {
            assembly {
                mstore(ready, count)
            }
        }
        return ready;
    }

    /**
     * @notice Injects funds into the streamers provided
   * @param ready the list of streamers to fund (addresses must be pre-approved)
   */
    function injectFunds(address[] memory ready) public whenNotPaused {
        uint256 minWaitPeriodSeconds = s_minWaitPeriodSeconds;
        IERC20 token = IERC20(s_injectTokenAddress);
        address[] memory streamerlist = s_streamerList;

        uint256 balance = token.balanceOf(address(this));
        Target memory target;

        for (uint256 idx = 0; idx < ready.length; idx++) {
            target = s_targets[ready[idx]];
            IChildChainStreamer streamer = IChildChainStreamer(streamerlist[idx]);
            if (
                target.lastInjectionTimeStamp + minWaitPeriodSeconds <= block.timestamp &&
                streamer.reward_data(address(token)).period_finish >= block.timestamp &&
                balance >= target.amountPerPeriod &&
                target.periodNumber < target.maxPeriods
            ) {
                bool success = token.transfer(s_feeDistributorAddress, target.amountPerPeriod);
                if (success) {
                    s_targets[ready[idx]].lastInjectionTimeStamp = uint56(block.timestamp);
                    s_targets[ready[idx]].periodNumber += 1;
                    try streamer.notify_reward_amount(address(token)) {
                        emit emissionsInjection(ready[idx], target.amountPerPeriod);
                    } catch {
                        revert("Failed to call notify_reward_amount");
                        emit injectionFailed(ready[idx]);
                    }
                } else {
                    emit injectionFailed(ready[idx]);
                }
            }
        }
    }

    /**
     * @notice Get list of addresses that are ready for new token injections and return keeper-compatible payload
   * @return upkeepNeeded signals if upkeep is needed, performData is an abi encoded list of addresses that need funds
   */
    function checkUpkeep(bytes calldata)
    external
    view
    override
    whenNotPaused
    returns (bool upkeepNeeded, bytes memory performData)
    {
        address[] memory ready = getReadyStreamers();
        upkeepNeeded = ready.length > 0;
        performData = abi.encode(ready);
        return (upkeepNeeded, performData);
    }

    /**
     * @notice Called by keeper to send funds to underfunded addresses
   * @param performData The abi encoded list of addresses to fund
   */
    function performUpkeep(bytes calldata performData) external override onlyKeeperRegistry whenNotPaused {
        address[] memory needsFunding = abi.decode(performData, (address[]));
        injectFunds(needsFunding);
    }

    /**
     * @notice Withdraws the contract balance
   * @param amount The amount of eth (in wei) to withdraw
   * @param recipient The address to pay
   */
    function withdrawGasToken(uint256 amount, address payable recipient) external onlyOwner {
        if (recipient == address(0)) {
            revert ZeroAddress();
        }
        emit gasTokenWithdrawn(amount, recipient);
        recipient.transfer(amount);
    }

    /**
     * @notice Streamers only have 1 admin/distributor which has to be this contract, this allows  passthrough management
    * @param _contract the contract to call
    * @param _data the calldata to forward to said contract
    */
    function forwardCall(address _contract, bytes calldata _data) external onlyOwner {
        (bool success, ) = _contract.call(_data);
        require(success, "Call failed");
        emit forwardedCall(_contract);
    }
    /**
     * @notice Sweep the full contract's balance for a given ERC-20 token
   * @param token The ERC-20 token which needs to be swept
   * @param recipient The address to pay
   */
    function sweep(address token, address recipient) external onlyOwner {
        uint256 balance = IERC20(token).balanceOf(address(this));
        emit ERC20Swept(token, recipient, balance);
        SafeERC20.safeTransfer(IERC20(token), recipient, balance);
    }

    /**
     * @notice Sets the keeper registry address
   */
    function setKeeperRegistryAddress(address keeperRegistryAddress) public onlyOwner {
        emit KeeperRegistryAddressUpdated(s_keeperRegistryAddress, keeperRegistryAddress);
        s_keeperRegistryAddress = keeperRegistryAddress;
    }

    /**
     * @notice Sets the minimum wait period (in seconds) for addresses between injections
   */
    function setMinWaitPeriodSeconds(uint256 period) public onlyOwner {
        emit MinWaitPeriodUpdated(s_minWaitPeriodSeconds, period);
        s_minWaitPeriodSeconds = period;
    }

    /**
     * @notice Gets the keeper registry address
   */
    function getKeeperRegistryAddress() external view returns (address keeperRegistryAddress) {
        return s_keeperRegistryAddress;
    }

    /**
     * @notice Gets the minimum wait period
   */
    function getMinWaitPeriodSeconds() external view returns (uint256) {
        return s_minWaitPeriodSeconds;
    }

    /**
     * @notice Gets the list of addresses on the in the current configuration.
   */
    function getWatchList() external view returns (address[] memory) {
        return s_streamerList;
    }

    /**
     * @notice Sets the address of the ERC20 token this contract should handle
   */
    function setInjectTokenAddress(address ERC20token) public onlyOwner {
        s_injectTokenAddress = ERC20token;
    }

    /**
    * @notice Sets the address the fee distributor this contract should send tokens to
   */
    function setFeeDistributorAddress(address recipient) public onlyOwner {
        s_feeDistributorAddress = recipient;
    }
    /**
     * @notice Gets configuration information for an address on the streamerlist
   */
    function getAccountInfo(address targetAddress)
    external
    view
    returns (
        bool isActive,
        uint256 amountPerPeriod,
        uint8 maxPeriods,
        uint8 periodNumber,
        uint56 lastInjectionTimeStamp
    )
    {
        Target memory target = s_targets[targetAddress];
        return (target.isActive, target.amountPerPeriod, target.maxPeriods, target.periodNumber, target.lastInjectionTimeStamp);
    }

    /**
     * @notice Pauses the contract, which prevents executing performUpkeep
   */
    function pause() external onlyOwner {
        _pause();
    }

    /**
     * @notice Unpauses the contract
   */
    function unpause() external onlyOwner {
        _unpause();
    }

    modifier onlyKeeperRegistry() {
        if (msg.sender != s_keeperRegistryAddress) {
            revert OnlyKeeperRegistry();
        }
        _;
    }
}
