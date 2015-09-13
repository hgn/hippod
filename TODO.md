
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
