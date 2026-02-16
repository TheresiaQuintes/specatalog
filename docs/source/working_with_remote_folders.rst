Working with remote directories
===============================

Setup
-----
Prerequisites: You are allowed to mount your remote folder via SMB


Linux
^^^^^
::

	nano ~/.smbcredentials_sr_nas
	
	username=usrname
	password=%%%%
	
	chmod 600 ~/.smbcredentials_sr_nas
	
	mkdir ~/NAS_SR_group
	
	in etc/fstab:
	//sr-nas.pc.intra.uni-freiburg.de/group/archive_specatalog  /home/USER/NAS_SR_group  cifs  credentials=/home/USER/.smbcredentials,vers=3.0,uid=1000,gid=1000,user,noauto,_netdev  0  0
	systemctl daemon-reload
	
	testen:
	mount ~/NAS_SR_group
	umount ~/NAS_SR_group
	
	in ~/.specatalog/defaults.json
	add:
	"mount_point" : /home/USER/NAS_SR_group
	
	(base_path = local_path)


Windows
^^^^^^^

::

	cmdkey /add:sr-nas.pc.intra.uni-freiburg.de /user:usrname /pass:%%%%

	testen:
	use P: \\sr-nas.pc.intra.uni-freiburg.de\group\archive_specatalog /persistent:no
	net use P: /delete
	
	in ~/.specatalog/defaults.json
	add:
	"mount_point" :  r"\\sr-nas.pc.intra.uni-freiburg.de\group\archive_specatalog"
	"//sr-nas.pc.intra.uni-freiburg.de/group/archive_specatalog"
	
	(base_path = local_path)


New commands
------------

specatalog-sync-download
specatalog-sync-upload
