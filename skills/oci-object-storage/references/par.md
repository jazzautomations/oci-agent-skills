# Pre-authenticated requests
Source: research/04c Object Storage; research/14 §8.
A PAR is a bearer credential, independent of a consumer's OCI login. Choose the narrowest object/prefix and read/write mode for the actual sharing request; set an explicit expiry.
The access URI appears only at creation. Never record it in a repository, report or console log. List metadata to diagnose expiry and deletion; this cannot recover a lost URI.
Renewal requires a new PAR and consumer migration. Revoke only the specific PAR after authorization, with acknowledgement that the previous URL cannot be restored. A public bucket is not a substitute for a narrowly scoped PAR.
