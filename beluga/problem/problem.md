To generate the instance.json that is showed in this problem folder, first of all, place yourself in the terminal within the beluga folder of this repository, then, make sure that the problem folder exists, if not, create it, then, activate your environment and execute the following line:

python3 generate_instance.py -s 2026 -or 50.0 -t 0 -f 150 -v -o problem/ -on instance.json -pp -pm arrivals

After this, an instance.json within the problem folder is created, to generate instance.pddl and domain.pddl from instance.json, perform the following:

python3 json2PDDL.py -i problem/instance.json -o problem/

After this, the required PDDL files are created, representing the problem and corresponding probabilistic domain. These files represent the task to be solved.
