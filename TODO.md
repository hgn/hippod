
- [ ] Check disk utilization and show at admin dashboard
- [ ] Implement grahs using: visjs and chartjs.
- [ ] The server can provide an API to return the actual time. This time can
  be used by the clients to check if the time is not up-to-date. The
	user can be informed to update the time and the upload can probably be
	restricted if not in sync with the server.
- [ ] There is no **version** field in the achievement. There should be some
  version info what is tested. The problem with the version is that these must
	be abolutely correct. E.g. the user will miss to update the version - so it
	must be auto-generated or queried from the version control system (e.g. git id).
	So this is a must. Another problem is that larger software components consist of
	many packages, each with a own version. Which one is now the major one? This is not
	the problem which should be solved in contestcolld! Currently I have no ideal solution
	to this problem so the versioning is left out for upcoming versions.
- [ ] Provide a knob to configure the maximum number of attachments and data per see.
  If limit is reached a HTTP error code MUST be returned. This knob can be on a per
	attachment basis and on a per object basis. E.g. to limit wild scripts. Another
	idea is to limit this on a per category basis. Probably on a per user basis? Overall
	maximum limit? This can all be presented on the admin panel. Hard quota
- [ ] Private User Concept (Incognito Mode) - Users (concrete Submitter) should
	be switched into a private mode. E.g. during developing these user test
	results are not displayed in the statistics and any other output. The
	generated tests nevertheless added and collected. If Incognito mode is
	disabled later all results are displayed. The idea behind is that the user
	should do their tests even when they are in heavy debugging mode.
- [ ] Result compression feature. Should the webgui collect several good and/or
	bad results and show only one result (e.g. with the number of successive
	failed/passed)? Idea is that there is no real gain to see when everything
	works for a while.
