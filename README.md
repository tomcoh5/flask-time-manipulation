# flask-time-manipulation
## Applcation setup
There are two docker containers (python based image) that are connected with volume. When you click in the main website (the first container) it will write to a file (named "time.txt") simple string + newline . The second container will read the file , count the number of lines and calculate num_of_lines multiply by 5.It will then take the exact time that you login to the website (datetime.datetime.now) and will subtract the number_oflines multiply by 5, that will be the output in the website.
## CI CD TOOL
The ci cd i chose was jenkins , mostly because of two reasons.
The first reason is that i have an exeprience with this ci cd tool.
The second reason is that has huge community (lot of documentation and support online)
# CICD steps
git clone -> building dockerimages -> testing (curl command) -> uploading to ecr (aws) -> deploying using ecs-cli (aws)
