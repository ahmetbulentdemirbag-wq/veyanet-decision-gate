# GitHub Upload Steps

Use these steps to create the public 24/7 links needed for Devpost judging.

## 1. Create The Repository

Create a new GitHub repository:

```text
Repository name: veyanet-decision-gate
Owner: ahmetbulentdemirbag-wq
Visibility: Public
Add README: No
Add .gitignore: No
Add license: No
```

Expected repository URL:

```text
https://github.com/ahmetbulentdemirbag-wq/veyanet-decision-gate
```

## 2. Upload Files

Unzip `VeyaNet_Decision_Gate_Repo_Root_Upload.zip`.

Upload the extracted files and folders to the repository root. The repository root must contain:

```text
index.html
README.md
assets/
presentation/
screenshots/
DEVPOST_SUBMISSION.md
LINK_CHECKLIST.md
YOUTUBE_VIDEO_GUIDE.md
LICENSE
.nojekyll
```

Do not upload the ZIP itself as the only repository content. GitHub Pages needs `index.html` at the root.

## 3. Enable GitHub Pages

Open the repository:

```text
Settings -> Pages
```

Set:

```text
Source: Deploy from a branch
Branch: main
Folder: /root
```

Save.

Expected live demo URL:

```text
https://ahmetbulentdemirbag-wq.github.io/veyanet-decision-gate/
```

## 4. Devpost Links

Use these in Devpost after they are live:

```text
Code repository:
https://github.com/ahmetbulentdemirbag-wq/veyanet-decision-gate

Live demo:
https://ahmetbulentdemirbag-wq.github.io/veyanet-decision-gate/

YouTube demo:
PASTE_PUBLIC_YOUTUBE_LINK_HERE
```

## 5. Final Check

Open the live demo link in an incognito/private browser window. If it opens without login, judges can see it 24/7.
