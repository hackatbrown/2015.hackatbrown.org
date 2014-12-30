# Dev Instructions

Dev expected parameters:
`application: hackatbrown2015
version: 9`

Always push to `dev`. Remember the dev server has the SAME datastore as the master one. Then merge into `master`, and make sure the version number in `app.yaml` is 2. Then deploy.

For additional testing at scale, we also have a QA branch & server. Annoyingly, it's named `hackatbrown2015-dev`. It should be version 9. It does NOT share a datastore with the other 2 servers.

Follow these instructions:
- `git checkout dev`
- `git pull`
- Make your changes
- `git add -A`
- `git commit -m "Message"`
- `git push`
- `git checkout master`
- `git pull`
- `git merge dev`
- Check to make sure version in `app.yaml` is 2
- `git push`
- Deploy via Google App Engine Launcher
