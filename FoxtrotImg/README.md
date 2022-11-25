# FoxBot
Twitter bot posting daily Foxtrot strips from gocomics.com.

- Downloads images to .\FoxtrotImg
- Executes the upload of images and the posting of tweets using twurl

# To run locally:
1. Install twurl [here](https://github.com/twitter/twurl)
2. Set up your dev account with Twitter [here](https://developer.twitter.com/)
3. Authenticate with twurl using
 `twurl authorize --consumer-key key --consumer-secret secret`