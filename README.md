# finalProjectLog8415
LOG8415 (Advanced Concepts Of Cloud Computing) final project : Fully automated website deployment tool (Polytechnique Montreal)

## Run the default scenario (with provided website) 

To run the deployment tool, please install Python 3.  Then run the following commands to install dependencies:
```
  $ pip install boto3
  $ pip install paramiko
  $ pip install scp
```
Then download and extract the ZIP file containing the code,  or clone this repository. Next configure all the variables, at the top of the file deploy.py.  Once it is done, simply run (change pathtodeploy.pyfileby the path of the file):

```
  $ cd path_to_deploy.py_file
  $ py ./deploy.py

```

The website will be deployed on AWS !
