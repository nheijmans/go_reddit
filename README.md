# Reddit Data Collector
### Introduction
With this SAM template you can collect the new/recent **posts** from your favorite subreddits. The data is stored in an S3 bucket. Every subreddit is written to its own CSV file. 
The intend is to rewrite this to a Go application. To be continued. 

### Customizing
In the ```reddit_scraper.py``` file on line 14, *TOPICS*, add the subreddits you want to collect in the list object. 
Done :) 

### Deploying
Easy peasy with AWS SAM
```
sam deploy --guided
```

### Credits
Lambda completely written by [@achernyshova]( https://github.com/achernyshova/Reddit-NLP-Classification ). Just added it to a SAM Template for easier deployment and updating. 