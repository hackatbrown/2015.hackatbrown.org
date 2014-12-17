# Dev Instructions

Dev expected parameters:
`application: hackatbrown2015
version: 9`

Always push to `dev`. Then merge into `master`, and make sure the version number in `app.yaml` is 2. Then deploy.

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
