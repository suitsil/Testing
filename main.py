from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import uvicorn

app = FastAPI(title="Student Application Testing System")

# In-memory storage
students = {}
tests = {}
test_results = []

# Pydantic Models
class Student(BaseModel):
    id: int = Field(..., description="Unique identifier for the student")
    name: str = Field(..., min_length=2, max_length=50, description="Student's full name")
    email: str = Field(..., description="Student's email address")
    tests_taken: List[int] = []

class Test(BaseModel):
    id: int = Field(..., description="Unique identifier for the test")
    name: str = Field(..., min_length=2, max_length=100, description="Name of the test")
    max_score: int = Field(..., description="Maximum possible score")

class TestResult(BaseModel):
    student_id: int = Field(..., description="ID of the student taking the test")
    test_id: int = Field(..., description="ID of the test taken")
    score: int = Field(..., description="Score obtained in the test")

class ResponseMessage(BaseModel):
    message: str

# 1. Create a Student
@app.post("/students/", response_model=Student)
async def create_student(student: Student):
    if student.id in students:
        raise HTTPException(status_code=400, detail="Student with this ID already exists")
    students[student.id] = student
    return student

# 2. Get a Student by ID
@app.get("/students/{student_id}/", response_model=Student)
async def get_student(student_id: int):
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    return students[student_id]

# 3. Get All Students
@app.get("/students/", response_model=List[Student])
async def get_all_students():
    return list(students.values())

# 4. Create a Test
@app.post("/tests/", response_model=Test)
async def create_test(test: Test):
    if test.id in tests:
        raise HTTPException(status_code=400, detail="Test with this ID already exists")
    tests[test.id] = test
    return test

# 5. Get a Test by ID
@app.get("/tests/{test_id}/", response_model=Test)
async def get_test(test_id: int):
    if test_id not in tests:
        raise HTTPException(status_code=404, detail="Test not found")
    return tests[test_id]

# 6. Get All Tests
@app.get("/tests/", response_model=List[Test])
async def get_all_tests():
    return list(tests.values())

# 7. Submit Test Result
@app.post("/results/", response_model=TestResult)
async def submit_test_result(result: TestResult):
    if result.student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    if result.test_id not in tests:
        raise HTTPException(status_code=404, detail="Test not found")
    if result.score > tests[result.test_id].max_score:
        raise HTTPException(status_code=400, detail="Score exceeds maximum possible score")
    
    test_results.append(result)
    students[result.student_id].tests_taken.append(result.test_id)
    return result

# 8. Get All Test Results for a Student
@app.get("/results/student/{student_id}/", response_model=List[TestResult])
async def get_student_results(student_id: int):
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    return [result for result in test_results if result.student_id == student_id]

# 9. Get All Test Results for a Specific Test
@app.get("/results/test/{test_id}/", response_model=List[TestResult])
async def get_test_results(test_id: int):
    if test_id not in tests:
        raise HTTPException(status_code=404, detail="Test not found")
    return [result for result in test_results if result.test_id == test_id]

# 10. Get Average Score for a Test
@app.get("/results/test/{test_id}/average", response_model=dict)
async def get_average_score(test_id: int):
    if test_id not in tests:
        raise HTTPException(status_code=404, detail="Test not found")
    test_scores = [result.score for result in test_results if result.test_id == test_id]
    if not test_scores:
        raise HTTPException(status_code=404, detail="No results found for this test")
    average = sum(test_scores) / len(test_scores)
    return {"test_id": test_id, "average_score": average}

# 11. Get Highest Score for a Test
@app.get("/results/test/{test_id}/highest", response_model=dict)
async def get_highest_score(test_id: int):
    if test_id not in tests:
        raise HTTPException(status_code=404, detail="Test not found")
    test_scores = [result.score for result in test_results if result.test_id == test_id]
    if not test_scores:
        raise HTTPException(status_code=404, detail="No results found for this test")
    highest = max(test_scores)
    return {"test_id": test_id, "highest_score": highest}

# 12. Delete a Student by ID
@app.delete("/students/{student_id}/", response_model=ResponseMessage)
async def delete_student(student_id: int):
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    del students[student_id]
    global test_results
    test_results = [result for result in test_results if result.student_id != student_id]
    return {"message": f"Student with ID {student_id} deleted successfully"}

# Run the application
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)