Working with remote directories
===============================

If you want to have a shared archive folder with your group the following instructions for the setup of a remote folder might be helpful.

Prerequisites:
--------------
- A directory that is remotely saved
- All group members are allowed to mount this folder via SMB
- All members have read/write access to the folder


First Setup
-----------

Linux
^^^^^

1. Create a smb-credentials file::
	
	nano ~/.smbcredentials_specatalog
	
Fill the file with your access data for the remote folder::
	
	username=usrname
	password=%%%%

2. Change the visibility::
	
	chmod 600 ~/.smbcredentials_sr_nas

3. Create a new folder as a mount point::
	
	mkdir ~/tmp_archive_mount

4. Add an entry to the /etc/fstab::
	
	//sr-nas.pc.intra.uni-freiburg.de/group/archive_specatalog  /home/USER/tmp_archive_mount  cifs  credentials=/home/USER/.smbcredentials_specatalog,vers=3.0,uid=1000,gid=1000,user,noauto,_netdev  0  0

(You can find your uid/gid by typing ``id`` to your terminal)

5. Reload fstab::

	systemctl daemon-reload
	
6. Test mounting the remote folder::

	mount ~/tmp_archive_mount
	umount ~/tmp_archive_mount

7. Open the defaults-file

	::
	
		nano ~/.specatalog/defaults.json
		
	and add::

		"mount_point" : /home/USER/tmp_archive_mount
		
	The ``base_path`` should be a local folder on your system.


Windows
^^^^^^^

1. Add your access data to the remote folder::

	cmdkey /add:sr-nas.pc.intra.uni-freiburg.de /user:usrname /pass:%%%%

2. Test mounting the remote folder::

	use P: \\sr-nas.pc.intra.uni-freiburg.de\group\archive_specatalog /persistent:no
	
	net use P: /delete

3. Open the defaults-file in an editor
	
	::

		~/.specatalog/defaults.json
	

	and add::

		"mount_point" :  "\\\\sr-nas.pc.intra.uni-freiburg.de\\group\\archive_specatalog"
		
	The ``base_path`` should be a local folder on your system.


New commands
------------

You can now snchronise your local directory with the remote folder via the CLI-commands::

	specatalog-sync-download
	specatalog-sync-upload

.. caution::
	
	Before you run ``specatalog-sync-upload`` for the first time make sure that you have downloaded the remote folder before (``specatalog-sync-download``) Otherwise the remote folder will be overwritten by your (empty) local folder!

