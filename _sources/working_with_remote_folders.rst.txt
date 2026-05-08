Working with remote directories
===============================

If you want to have a shared archive folder with your group the following instructions for the setup of a remote folder might be helpful.

Prerequisites:
--------------
- All collaborators have installed syncthing (running)
- At least one collaborator has an initial archive directory that shall be shared


Install and activate syncthing
------------------------------

Linux (Ubuntu)
^^^^^^^^^^^^^^

Run the following commands::

   sudo apt install syncthing
   systemctl --user enable syncthing
   systemctl --user start syncthing




Synchronise the archive directory
---------------------------------
1. Create an empty folder (this will be your archive directory).

2. Open the web interface of syncthing at `<http://localhost:8384>`_.

3. Click on "add folder" and add your empty archive directory

   Make sure, that the "Folder ID" ("Ordnerkennung") has the name ``specatalog_archive``

   Choose the "Trash Can File Versioning" and set the deletion e.g. to 30 days.

4. Now you have to talk to your collaborators:

   - Ask them for their Device ID and tell them yours (Actions -> Own ID)
   - You and your collaborators are now able to add each other as remote devices using the Device ID
   - Set your archive directory as shared folder.