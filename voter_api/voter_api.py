import json
from flask import Flask, request, jsonify

app = Flask(__name__)


# This function queries a voter's record
@app.route('/students/get_voter', methods=['GET'])
def get_voter():
    voter_record = json.loads(request.data)
    student_id = request.args.get('student_id')

    with open('students.txt', 'r') as f:
        data = f.read()
        voter_records = json.loads(data)
        found = False
        for voter in voter_records:
            if voter['student_id'] == student_id:
                found = True
                return jsonify(voter)
            elif 'student_id' in voter_record:
                if voter['student_id'] == voter_record['student_id']:
                    found = True
                    return jsonify(voter)
        if not found:
            return jsonify({'error': 'voter cannot be found'}), 404


# This function creates a voter
@app.route('/students/create_voter', methods=['POST'])
def create_voter():
    voter_records = json.loads(request.data)

    with open('students.txt', 'r') as f:
        data = f.read()

    if not data:
        records = [voter_records]
    else:
        records = json.loads(data)
        for record in records:
            if record['student_id'] == voter_records['student_id']:
                return jsonify({'error': 'There is a duplicate Student ID'}), 400
        records.append(voter_records)

    with open('students.txt', 'w') as f:
        f.write(json.dumps(records, indent=2))
    return jsonify(voter_records), 201


# This function is responsible for updating a voter's record
@app.route('/students/update_voter', methods=['POST'])
def update_voter():
    record = json.loads(request.data)
    new_records = []

    with open('students.txt', 'r') as f:
        data = f.read()
        records = json.loads(data)
        found = False

    for rec in records:
        if rec['student_id'] == record['student_id']:
            found = True
            if 'year' in record:
                rec['year'] = record['year']
            if 'major' in record:
                rec['major'] = record['major']
            if 'name' in record:
                rec['name'] = record['name']

        new_records.append(rec)

    if not found:
        return jsonify({'error': 'data not found'}), 404

    with open('students.txt', 'w') as f:
        f.write(json.dumps(new_records, indent=2))
    return jsonify(record)


# This function is responsible for deleting a voter from the records
@app.route('/students/delete_voter', methods=['DELETE'])
def delete_voter():
    record = json.loads(request.data)
    new_records = []

    with open('students.txt', 'r') as f:
        data = f.read()
        records = json.loads(data)
        found = False

        for rec in records:
            if rec['student_id'] == record['student_id']:
                found = True
                continue
            new_records.append(rec)

        if not found:
            return jsonify({'error': 'The data cannot be found'}), 404

        with open('students.txt', 'w') as f:
            f.write(json.dumps(new_records, indent=2))

    return jsonify(''), 204


# This function is responsible for querying an election
@app.route('/elections/get_election', methods=['GET'])
def get_election():
    record = json.loads(request.data)
    id = request.args.get('election_id')

    if 'election_id' not in record and not id:
        return jsonify({'error': 'election ID is missing'}), 400

    with open('elections.txt', 'r') as f:
        data = f.read()
        records = json.loads(data)
        found = False

    for record in records:
        if 'election_id' in record:
            if record['election_id'] == record['election_id']:
                found = True
                return jsonify(record)
        elif record['election_id'] == id:
            found = True
            return jsonify(record)

    if not found:
        return jsonify({'error': 'The data cannot be found'}), 404


# This function is responsible for creating an election
@app.route('/elections/create_election', methods=['POST'])
def create_election():
    record = json.loads(request.data)

    if 'election_id' not in record:
        return jsonify({'error': 'Missing field electionID in JSON data'}), 400
    if 'candidates' not in record:
        return jsonify({'error': 'Missing field candidates in JSON data'}), 400

    with open('elections.txt', 'r') as f:
        data = f.read()

    if not data:
        records = [record]

    else:
        records = json.loads(data)
        for rec in records:
            if rec['election_id'] == record['election_id']:
                return jsonify({'error': 'Duplicate electionID'}), 400
        records.append(record)

    with open('elections.txt', 'w') as f:
        f.write(json.dumps(records, indent=2))
    return jsonify(record), 201


# This function is responsible for deleting an election
@app.route('/elections/delete_election', methods=['DELETE'])
def delete_election():
    record = json.loads(request.data)
    new_records = []

    if 'election_id' not in record:
        return jsonify({'error': 'election ID is missing'}), 400

    with open('elections.txt', 'r') as f:
        data = f.read()
        records = json.loads(data)
        found = False

        for rec in records:
            if rec['election_id'] == record['election_id']:
                found = True
                continue
            new_records.append(rec)
    if not found:
        return jsonify({'error': 'The data cannot be found'}), 404

    with open('elections.txt', 'w') as f:
        f.write(json.dumps(new_records, indent=2))
    return jsonify(''), 204


# This function is responsible for the voting process
@app.route('/elections/vote', methods=['PATCH'])
def vote():
    record = json.loads(request.data)
    students_voted = []
    print(record['election_id'])
    print(record['candidate_id'])
    if 'election_id' not in record:
        return jsonify({'error': 'Missing field electionID in JSON data'}), 400
    elif 'student_id' not in record:
        return jsonify({'error': 'Missing field studentID in JSON data'}), 400
    elif 'candidate_id' not in record:
        return jsonify({'error': 'Missing field candidateID in JSON data'}), 400

    with open('elections.txt', 'r') as f:
        data = f.read()
        records = json.loads(data)
    with open('students.txt', 'r') as f:
        student_data = f.read()
        students = json.loads(student_data)
    found = False
    for student in students:
        if student['student_id'] == record['student_id']:
            found = True

            for rec in records:
                if rec['election_id'] == record['election_id']:
                    if rec['candidate_id'] not in record['candidates']:
                        return jsonify({"error": "A valid candidate wasn't given"}), 400

                    if 'students_voted' not in record:
                        rec['students_voted'] = []  # Stores the ID's of students that have voted

                    if rec['student_id'] not in record['students_voted']:
                        if 'votes' not in record:
                            rec['votes'] = {}  # stores votes and the student ID as a key-value pair
                            if rec['candidate_id'] not in record['votes']:
                                rec['votes'][record['candidate_id']] = 1
                                rec['students_voted'].append(record['student_id'])
                        else:
                            if rec['candidate_id'] not in record['votes']:
                                rec['votes'][record['candidate_id']] = 1
                                rec['students_voted'].append(record['student_id'])
                            else:
                                rec['votes'][record['candidate_id']] += 1
                                rec['students_voted'].append(record['student_id'])
                    else:
                        return jsonify({"error": "The student has already voted"}), 400

                students_voted.append(rec)
    if not found:
        return jsonify({'error': "The student has not been registered"})

    with open('elections.txt', 'w') as f:
        f.write(json.dumps(students_voted, indent=2))

    return jsonify(students_voted)


app.run(debug=True)
