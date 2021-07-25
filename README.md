# flask-time-manipulation
## Applcation setup
There are two Docker containers (python based image) that are connected with volume. When you click in the main website (the first container) it will write to a file (named "time.txt") simple string + newline . The second container will read the file , count the number of lines and calculate num_of_lines multiply by 5.It will then take the exact time that you login to the website (datetime.datetime.now) and will subtract the number_oflines multiply by 5, that will be the output in the website.
## CI CD TOOL
The CICD I chose was Jenkins , mostly because of two reasons.
The first reason is that I an have exeprience with this CICD tool.
The second reason is that it has huge community (lot of documentation and support online)
# CICD steps
Git clone -> building Dockerimages -> testing (curl command) -> uploading to ECR (AWS) -> deploying using ECS-cli (AWS)
