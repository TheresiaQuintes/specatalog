Working with remote directories
===============================

Setup
-----

Linux
^^^^^
::

	nano ~/.smbcredentials_sr_nas
	
	username=usrname
	password=%%%%
	
	chmod 600 ~/.smbcredentials_sr_nas
	
	NÄCHSTE 2 SCHRITTE ANPASSEN: mkdir ~/tmp_archive -> NUR ARCHIVE-FOLDER EINHÄNGEN
	mkdir ~/NAS_SR_group
	
	in etc/fstab:
	//sr-nas.pc.intra.uni-freiburg.de/group/archive_specatalog  /home/USER/NAS_SR_group  cifs  credentials=/home/USER/.smbcredentials,vers=3.0,uid=1000,gid=1000,user,noauto,_netdev  0  0
	systemctl daemon-reload
	
	testen:
	mount ~/NAS_SR_group
	umount ~/NAS_SR_group
	
	mount_point = /home/USER/NAS_SR_group

