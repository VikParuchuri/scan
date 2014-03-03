Scan
-----------------------------------------

Scan is a lightweight server that allows for automated scoring of essays.

Installation
-----------------------------------------

# Vagrant



# Manual

Linux is currently the best supported platform, but it is also possible to install on windows.

## Ubuntu

```
xargs -a apt-packages.txt install -y
pip install -r pre-requirements.txt
pip install -r requirements.txt
```

## Windows


#. Install the scipy stack from [here](http://www.lfd.uci.edu/~gohlke/pythonlibs/#scipy-stack).
#. Install scikit-learn from the [same place](http://www.lfd.uci.edu/~gohlke/pythonlibs/#scikit-learn)



Please see install instructions here:

http://scikit-learn.org/0.9/install.html


Usage
------------------------------------------

```
nosetests --with-coverage --cover-package="core" --logging-level="INFO"
```