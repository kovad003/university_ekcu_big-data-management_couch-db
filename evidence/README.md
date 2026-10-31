# Evidence

Everything here is written by the scripts. Nothing is edited by hand. Each run of an experiment replaces its folder.

Run `python run.py` on the recording machine. When every check passes, commit the folder.

Per experiment, you get `transcript.md` (every request and the full response, with the instance named and passwords masked), `results.json` (each check with expected value, observed value and PASS/FAIL) and `record.md` (the experiment record from the course template). Some experiments also save JSON states: the common starting revision, the conflicting revisions and the resolved document. `timing.csv` appears only after `python run.py C --timing`.

Screenshots go in here too, named after the step they show.
