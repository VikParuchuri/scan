Scan
-----------------------------------------

Scan is an easy to use server that lets you score essays automatically.  Follow the quickstart instructions to get everything up and running.

Note:  This is a relatively new project.  It has good unit test coverage, and has some manual testing (not just by me), but please test it yourself before using in anything critical.

Installation
-----------------------------------------

# Quickstart

The easiest way to get started is with a Vagrant virtual machine:

First, [install VirtualBox](https://www.virtualbox.org/wiki/Downloads).

Next, [install Vagrant](http://www.vagrantup.com/downloads)

Then clone this repo.  If you are unfamiliar with git, please first [install git](http://git-scm.com/book/en/Getting-Started-Installing-Git) and then look at [the basics of cloning a repo](http://git-scm.com/book/en/Git-Basics-Getting-a-Git-Repository).

```sh
git clone https://github.com/VikParuchuri/scan.git
```

Then we have to navigate to the directory and start up vagrant from the command line:

```sh
cd scan
vagrant up
```

This should take 20-30 minutes to download and install dependencies on newer machines.

Congrats!  Visiting `http://127.0.0.1:5000` in your browser will now let you use Scan.

If you find yourself running out of memory on the virtualbox (if models fail to build), you will want to increase available memory by editing this line in the VagrantFile:

```sh
v.memory = 2048
```

# Manual

Linux is currently the best supported platform, but it is also possible to install on windows.

## Ubuntu

```sh
xargs -a apt-packages.txt install -y
pip install -r pre-requirements.txt
pip install -r requirements.txt
```

## Windows (untested)

1. Install the scipy stack from [here](http://www.lfd.uci.edu/~gohlke/pythonlibs/#scipy-stack).
2. Install scikit-learn from the [same place](http://www.lfd.uci.edu/~gohlke/pythonlibs/#scikit-learn).  Full install instructions are [here](http://scikit-learn.org/0.9/install.html).
3. pip install -r requirements.txt

## Usage

Running the web server:

```sh
python app.py
```

Running task worker, which does things like model creation and scoring:

```sh
celery -A app.celery worker --loglevel=debug -B
```

Running tests.  Test coverage of the core algorithm is high, but not of the web portion.

```sh
nosetests --with-coverage --cover-package="core" --logging-level="INFO"
```

First Steps
-----------------------------------------

Once you have everything setup and running, here are some steps to try:

1. Create an account
2. Login with your account
3. Click on "questions" to get to the questions list
4. Create a question using the form.
5. Click on "view essays" under the question to see more details.
6. Add essays using a csv file upload (there are two sample set of essays at data/test/censorship to use.  train_2.csv will take some time to make a model, and train_2_short will be much faster.)
7. Click on "create model and score essays"
8. It may take some time to create the model, but you will get a status prompt that auto-refreshes.
9. Add more essays and score them using the "score essay" button on each essay.  You will have to manually refresh the page after doing this to see the score.

*Note:  You will want to test results on essays that do not have an actual score.  Predicted scores on essays that have a score entered upfront will be misleadingly high!*

Enjoy!

Contributions
--------------------------------------------

Contributions are very welcome.  Please fork and pull request to contribute.

Contact
--------------------------------------------

Please open a github issue if you see a bug.  If you have a general question, feel free to contact vik.paruchuri@gmail.com.