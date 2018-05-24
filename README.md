# python-backup-ovh-telephony

A tool to backup telephony settings of your OVH account using python 3.

## Installation

The easiest way to install is using pipenv and git clone.

1. Clone and pipenv:

    ```bash
    $ git clone https://github.com/alkivi-sas/python-backup-ovh-telephony
    $ cd python-backup-ovh-telephony
    $ pipenv install
    $ pipenv shell
    ```

2. Change the conf file :

    ```bash
    $ cp backup.conf.example backup.conf
    $ vim backup.conf
    ```

So far only rootdir is defined


## Usage
From a terminal :

   ```bash
   $ which python       # ensure you are in venv
   $ ./backup.py --help # show help
   $ ./backup.py        # default path defined in conf, all groups

   # Advanced using groups
   $ ./backup.py --group nic-1 --group nic-2 --rootdir /tmp
   ```
