## Keeping Information Safe in Uncertain Times: How many copies is enough? ##

 1. Why should you care?
     - Digital information can disappear -- either on purpose or by accident
          - horror story: Gitlab
          - horror story: ... 
          - horror story: ... 
     - Traditional durability strategies fail: Cannot rely on offline storage for durability
	     - No storage media is reliable enough to store and forget
         - Media obsolecence is also a threat to this strategy
     - In practice the reliability of your storage technology is uncertain
         - Many threats to digital content can wipe out multiple copies simultaneously, and underlying connected risks are hard to observe
         - No good data to establish reliability of cloud services
         - Data on disk reliability is limited -- and in practice implies that caution is warranted
     - Good practice -- keep multiple copies in different places
     
1. The problem
      - Maintaining multiple copies costs $$ -- and there are lots of options -- number of copies, distribution, storage services, compression, verification strategies
      - What combinations of choices is most cost effective to prevent loss?
      - Formally -- for a certain risk of loss -- what's the optimal budget (or for a fixed budget, how much loss can you prevent with the right choices?)

1. The solution
 	- Quantitative simulation framework
    - Allows exploration of a wide range of strategies
    - Using a wide range of threat models -- from bit-rot to floods to financial collapse, using a hierarchical event based model
    - Calibrated to real-world threat levels
    
1. What curators should know (rewrite in terms of clickbait titles?)
	-  "three ain't enough" - for a wide range of threats want 4-6 copies
    -  "trust, but verify" -  copies don't help much unless you  check (and repair); more copies aren't needed if you do
    -  "leave no stone unturned" - audit systematically, not randomly or on-use
    -  "size matters -- but not as much as think" -- how to deal with document size
    -  "everybody let's get small" -- compression is a win, most of the time
    -  "two strange tips to " -- how to insure against correlated failure
    -  "lock your house but keep keys with the neighbors" -- how to encrypt without losing it all

1. What vendors should know
    - It's not enough to "go up to 11"  -- the problem with 11 nines - unitless numbers, meaningless measures, and no money where there mouth is
    - "Sunshine is the best disinfectant" -- how to report failure rates meaningfully
    - "a crowd pleaser for your customers" -- providing verifiable fixity without tears
    
1. What researchers should try to learn
    - Cryptographic/sophisticated adversary models
    - Estimating failure rates from observed data
    - Remote verification
    - Cost modeling of complex auditing strategies and n
    
