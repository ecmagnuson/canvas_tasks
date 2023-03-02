## How to use this program:

1. In Auth.json set your API_URL accordingly:
	- API_URL is your url for Canvas
	- i.e. https://canvas.wisc.edu/
	
2. In Auth.json set your API_KEY accordingly:
	- On the left hand side of your Canvas home page:
		+ Account > Settings
		
 	- Scroll down and click "New Access Token"
 	- Give it a name and expiration date 
 	- Generate token
	 	+ It will be a long string of characters
 	- Copy down the token and put it into Auth.json API_KEY
 	
3. Any file that you place into the `resources` directory will be copied into each students assignment, so if you have any sort of rubric or feedback sheet you can place it there.
4. Run the program and it will guide you through the process inside of a terminal.

