import streamlit as st
from pymongo import MongoClient

# MongoDB 연결 설정
MONGO_URI = "mongodb+srv://jsheek93:j103203j@cluster0.7pdc1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)

user_db = client["user_database"]
student_collection = user_db["student"]
users_collection = user_db["users"]

teacher_position_db = client["teacher_position"]
position_collection = teacher_position_db["position"]

highschool_db = client["highschool_db"]
classes_info_collection = highschool_db["classes_info"]

# 직책 목록 가져오기
positions = position_collection.find({}, {"_id": 0, "직책": 1})  # "_id" 필드는 제외하고, "직책" 필드만 가져옴
position_list = [item['직책'] for item in positions] 

# 초기 상태 설정
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "position" not in st.session_state:
    st.session_state.role = ""
if "name" not in st.session_state:
    st.session_state.name = ""

# 사용자 인증 함수
def authenticate_user(username, password):
    user = users_collection.find_one({"username": username, "password": password})
    if user:
        return user
    return None

# 회원가입 함수
def register_user(username, password, role, additional_info):
    user = {
        "username": username,
        "password": password,
        "name": additional_info.get("name", ""),
        "position": role
    }
    users_collection.insert_one(user)



# 메인 페이지 함수
def main_page():
    st.title("요의정고등학교 2025 고교학점제 강의평가록")
    st.write(f"안녕하세요, {st.session_state.name}님!({st.session_state.position})")
    # 로그아웃 버튼
    if st.button("로그아웃"):
        # 세션 초기화
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        

# 교사용 성적 관리 페이지 함수
def teacher_input_page():
    st.title("학생 성적 입력 페이지")
    if st.session_state.logged_in:
        
        stu_num = st.text_input("학번 입력")
        if stu_num:
            try:
                stu_num = int(stu_num)
                student = student_collection.find_one({"학번": stu_num})
                if student:
                    st.write(f"학생 이름: {student.get('이름')}")
                    # 과목 선택
                    classes_info = classes_info_collection.find({}, {"_id":0, "subject_name":1})
                    subject_list = [classes_info['subject_name'] for classes_info in classes_info]
                    selected_subject = st.selectbox("과목 선택", subject_list)
                    
                    # 수강 강좌 선택
                    if selected_subject:
                        
                        subject_doc = classes_info_collection.find_one({"subject_name": selected_subject})
                        
                        if subject_doc and "classes" in subject_doc:
                            # classes 배열에서 class_name 목록 생성
                            course_list = [cls.get("class_name", "강좌명 없음") for cls in subject_doc["classes"]]

                            if course_list:
                                selected_course = st.selectbox("수강 강좌 선택", course_list)
                            else:
                                st.warning("해당 과목에는 수강 강좌가 없습니다.")
                        else:
                            st.warning("해당 과목의 클래스 정보를 찾을 수 없습니다.")           
                        
                    else:
                        st.write("과목을 선택해주세요")
                    
                    # 성적 등급 선택
                    grade = st.selectbox("성적 등급", ["A", "B", "C", "F"])

                    if grade == "F":
                        feedback = "재수강이 필요합니다"
                    else:
                        feedback = st.text_area("피드백 입력")
                    

                    if st.button("성적 입력"):
                        evaluation = {
                            "학번": stu_num,
                            "이름": student['이름'],
                            "수강과목": selected_subject,
                            "수강강좌": selected_course,
                            "성적등급": grade,
                            "피드백": feedback
                        }
                        evaluation_collection.insert_one(evaluation)
                        st.success(f"{student['이름']} 학생의 성적이 등록되었습니다.")
                else:
                    st.error("학생 정보를 찾을 수 없습니다. 학번을 다시 입력해주세요.")
            except ValueError:
                st.error("유효한 학번을 입력해주세요.")
        else:
            st.write("학번을 입력해주세요.")
    else:
        st.error("로그인이 필요합니다.")


# 교사 성적 열람 페이지 함수
def teacher_grade_page():
    st.title("학생 성적 조회 페이지")
    if st.session_state.logged_in:
        search_option = st.selectbox("검색 기준", ["학번", "이름", "수강강좌"])
        search_value = st.text_input(f"{search_option} 입력")

        if st.button("조회"):
            if search_option == "학번":
                query = {"학번": search_value}
            elif search_option == "이름":
                query = {"이름": search_value}
            elif search_option == "수강강좌":
                query = {"수강강좌": search_value}

            results = evaluation_collection.find(query)
            results_list = list(results)

            if results_list:
                for result in results_list:
                    st.write(f"학번: {result['학번']}")
                    st.write(f"이름: {result['이름']}")
                    st.write(f"수강과목: {result['수강과목']}")
                    st.write(f"수강강좌: {result['수강강좌']}")
                    st.write(f"성적등급: {result['성적등급']}")
                    st.write(f"피드백: {result['피드백']}")
                    st.write("---")
            else:
                st.error("해당 정보를 찾을 수 없습니다.")
    else:
        st.error("로그인이 필요합니다.")


# 로그인 상태에 따른 페이지 표시
if not st.session_state.logged_in:
    st.title("온양고등학교 2025 고교학점제 강의평가록")
    st.title("로그인 및 회원가입 시스템")
    choice = st.selectbox("메뉴 선택", ["로그인", "회원가입"])

    if choice == "로그인":
        username = st.text_input("아이디", key="login_username")
        password = st.text_input("비밀번호", type="password", key="login_password")
        if st.button("로그인"):
            user = authenticate_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.name = user.get("name")
                st.session_state.position = user.get("position")
                st.success(f"환영합니다, {st.session_state.name} 선생님! ({st.session_state.position})")
                
            else:
                st.error("아이디 또는 비밀번호가 잘못되었습니다.")

    elif choice == "회원가입":
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        confirm_password = st.text_input("비밀번호 확인", type="password")
        additional_info = {"name": st.text_input("이름")}
        role = st.selectbox("직책", position_list)

        if st.button("회원가입"):
            if password != confirm_password:
                st.error("비밀번호가 일치하지 않습니다.")
            else:
                register_user(username, password, selected_position, additional_info)
                st.success("회원가입이 완료되었습니다! 로그인하세요.")
else:
    # 로그인 성공 후 사이드바 메뉴 추가
  
    with st.sidebar:
        page = st.selectbox("페이지 선택", ["메인 페이지", "학생 성적 입력", "학생 성적 조회"])
    
    # 선택한 페이지로 이동
    if page == "메인 페이지":
        main_page()
    elif page == "학생 성적 입력":
        teacher_input_page()
    elif page == "학생 성적 조회":
        teacher_grade_page()
