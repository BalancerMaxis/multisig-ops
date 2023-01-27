## Balancer Maxi Multisig Handling FAQ


### What happens if a snapshot is posted on a day other than Thursday, or fails to meet other specifcations?
The Balancer Maxis are mandated by [BIP-163](https://snapshot.org/#/balancer.eth/proposal/0xcd2cab0522b0e9a90ad40f93aca4505b17d60468224c22b69c4f9bd2bbd64e31) to reject
any governance that does not meet specifications.  The Maxi's will check all posted BIPs on Friday.  We will contact
the OP of the Forum Post of any BIPs found not to be compliance, inviting them to remove their snapshot, and help them
to correct any problems and post a new snapshot the following week.   If the problems are only with the payload,
the PR can be modified while the vote is open.  
Application of final payloads will always be pending a final review my the Maxis.  Any governance approved BIPs
that are rejected by due to problems with specification will receive support in resubmitting the vote in the following
week. 

### When posting a snapshot, what must I ensure?
The following text is copied from [BIP-163](https://snapshot.org/#/balancer.eth/proposal/0xcd2cab0522b0e9a90ad40f93aca4505b17d60468224c22b69c4f9bd2bbd64e31):

Any address with over 200,000 veBAL held or in delegation may create a new snapshot vote directly on the snapshot forum. With great power comes great responsibility. Snapshot posters are expected to ensure the following:

- The Snapshot body should begin with a link to the transaction payload PR on github.  Followed by the full text of the BIP. If the text is too long, it can be truncated.
  - Note that if the proposal requires no on-chain actions to be executed, the payload is not required.
- A link to the forum discussion should be included in the discussion (optional) field of Snapshot.
- The Snapshot is titled like BIP-[XXX] Title from Forum, where XXX is the next number in the BIP sequence.
- The Original Forum Poster should update their post to match the title from the snapshot and include a link to it at the bottom of the body of the Forum Post.
- Barring clear community consensus otherwise the vote Should be of Type “Basic Voting” and the choices should be one of [Yes, let’s do it - No, This is not the way - Abstain].
- Runs for 96 hours starting on a Thursday (GMT).
- Has a quorum of 2 million veBAL.

Go through this list.  Make sure that every one of these statements is definitively true.

### How to I get this Snapshot JSON PR?
You can find instructions and examples [HERE](BIPs/00examples/).  You can also ask the Balancer Maxis for support.  They
will be happy to help you build your JSON and create a PR.  Just hop into the [Balancer Discord](ttps://discord.balancer.fi/)

### I have another Question
Come ask us and remind us to add it to this FAQ