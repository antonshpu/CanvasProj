async function load_courses(){
    // remove hidden from course frame
    // or this will not work
    const course_parent = document.getElementById("course-selector");
    const frame = document.getElementById("visual-course-box");

    const response = await fetch('/api/courses');
    const c_dict = await response.json();

    const courses = Object.keys(c_dict).map(id => {
        return {
            id: id,
            code: c_dict[id].code,
            name: c_dict[id].name  
        };
    });

    frame.innerHTML = '<div class="course-title">Your courses</div>';

    const response_selected_course = await fetch('/api/select_course');
    const response_selected_course_data = await response_selected_course.json();

    const course_selected_id = response_selected_course_data.course_editing_id;

    courses.forEach(course => {
            const btn = document.createElement('button');
            btn.className = 'course-button';
            btn.textContent = `${course.code} : ${course.name}`;
            frame.appendChild(btn);

            if (course_selected_id === course.id) {
                btn.classList.add("selected-btn");
            }

            btn.onmouseenter =()=>{
                btn.textContent = `${course.code} : ${course.name}, ID: ${course.id}`;
            }
            btn.onmouseleave =()=>{
                btn.textContent = `${course.code} : ${course.name}`;
            }

            btn.onclick = async () => {
                const response = await fetch('/api/select_course', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ course_code: course.code.trim(), id: course.id })
                });

                const text = await response.text();
                const result = JSON.parse(text);

                if (result[0] === "Successful course selection") {
                    const course_buttons = document.querySelectorAll("#visual-course-box .course-button");

                    course_buttons.forEach(course_button => {
                        if(course_button.classList.contains("selected-btn")){
                            course_button.classList.remove("selected-btn");
                        }
                    });

                    btn.classList.add("selected-btn");
                }
            }

            const remove = document.createElement('button');
            remove.className = 'course-button';
            remove.textContent = `Remove ${course.code}`;
            remove.style.backgroundColor = "red";
            remove.style.transform = "scale(0.5)";
            remove.style.padding = "200px -200px";
            remove.style.marginTop = "-20px";
            remove.style.marginBottom = "-20px";

            remove.onclick = async () => {
                const response = await fetch('/api/remove_course', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ course_code: course.code.trim(), id: course.id })
                });

                const text = await response.text();
                const result = JSON.parse(text);

                if (result[0] === "Succesful course removal") {
                  await load_courses();
                }
            }
            frame.appendChild(remove);
        });
    
    const add_input = document.createElement('input');
    add_input.className = 'course-button';
    add_input.id = 'new-course-input';
    add_input.style.transform = "scale(0.9)";
    add_input.placeholder = 'Add new course...';
    add_input.style.textAlign = "center";
    frame.appendChild(add_input);

    const add_confirm = document.createElement('button');
    add_confirm.className = 'course-button';
    add_confirm.id = 'new-course-confirm';
    add_confirm.style.transform = "scale(0.7)";
    add_confirm.style.textAlign = "center";
    add_confirm.textContent = 'Confirm';
    frame.appendChild(add_confirm);

    add_confirm.onclick = async () => {

        const del_response = await fetch('/api/add_course', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ course_code: add_input.value.trim() })
        });

        const text = await del_response.text();
        const result = JSON.parse(text);

        if (result[0] === "Succesful course creation") {
            add_input.value = '';
            add_input.placeholder = "Added!";
            await load_courses();
        } else {
            add_input.value = '';
            add_input.placeholder = result[0] || "Error: Course Not Found";
            add_input.style.borderColor = "red";
        }
    }
}

function drawLine(x1, y1, x2, y2) {
    const svg = document.getElementById('svg-canvas');
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", x1 + 150);
    line.setAttribute("y1", y1 + 65); 
    line.setAttribute("x2", x2);
    line.setAttribute("y2", y2 + 65);
    line.setAttribute("stroke", "#001a6e");
    line.setAttribute("stroke-width", "3");
    svg.appendChild(line);
}

function drawAllStems(rootNode) {
    const svg = document.getElementById('svg-canvas');
    if (!svg) return;
    
    svg.innerHTML = '';
    
    function traverse(node) {
        if (!node || !Array.isArray(node)) return;

        const [name, type, children, pos] = node;

        if (!pos || !Array.isArray(pos)) return;

        if (children && Array.isArray(children)) {
            children.forEach(child => {
                if (child && Array.isArray(child) && child[3]) {
                    drawLine(pos[0], pos[1], child[3][0], child[3][1]);
                    
                    traverse(child);
                }
            });
        }
    }
    
    if (rootNode) {
        traverse(rootNode);
    }
}

const render_node = (node, container, root_data) => {
    const [name, max_points, children, pos, weightage] = node;
    const [x, y] = pos;

    const wrapper = document.createElement('div');
    wrapper.className = 'node-wrapper';
    wrapper.style.position = 'absolute';
    wrapper.style.left = `${x}px`;
    wrapper.style.top = `${y}px`;
    wrapper.style.display = 'flex';
    wrapper.style.alignItems = 'center';
    wrapper.style.gap = '10px';       

    const actionBtn = document.createElement('button');
    actionBtn.className = 'node-action-btn';
    actionBtn.textContent = '+';
    actionBtn.classList.add("course-button");
    actionBtn.style.padding= "15px 10px";

    actionBtn.onclick = async () => {

        const newChild = [
            "New Task", 
            0, 
            [],
            [x + 200, y],
            0 
        ];

        if (!node[2]) node[2] = []; 
        node[2].push(newChild);

        const response = await fetch('/api/grade_schema', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(root_data)
        });

        if (response.ok) {
            load_course_editor();
    }
    };

    const box = document.createElement('div');
    box.className = 'grade-box';
    box.style.width = '175px';
    box.style.height = '135px';
    box.style.display = 'flex';
    box.style.flexDirection = 'column';
    box.style.justifyContent = 'center';
    box.style.padding = '10px';
    box.style.boxSizing = 'border-box';
    box.classList.add("course-button");

    box.onmousedown = (e) => {
        e.preventDefault();

        let offsetX = e.clientX - wrapper.offsetLeft;
        let offsetY = e.clientY - wrapper.offsetTop;

        function mouseMoveHandler(e) {
            let newX = e.clientX - offsetX;
            let newY = e.clientY - offsetY;
            
            wrapper.style.left = `${newX}px`;
            wrapper.style.top = `${newY}px`;
            
            node[3] = [newX, newY]; 

            if (typeof drawAllStems === 'function') {
                drawAllStems(root_data);
            }
        }

        async function mouseUpHandler() {
            document.removeEventListener('mousemove', mouseMoveHandler);
            document.removeEventListener('mouseup', mouseUpHandler);

            await fetch('/api/grade_schema', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(root_data)
            });
        }

        document.addEventListener('mousemove', mouseMoveHandler);
        document.addEventListener('mouseup', mouseUpHandler);
    };

    if(name !== "Master"){
        const removeBtn = document.createElement('button');
        removeBtn.className = 'node-remove-btn';
        removeBtn.innerHTML = 'X';
        removeBtn.style.position = 'absolute';
        removeBtn.style.top = '10px';
        removeBtn.style.right = '10px';
        removeBtn.style.width = '20px';
        removeBtn.style.height = '20px';
        removeBtn.style.borderRadius = '50%';
        removeBtn.style.backgroundColor = '#ff4d4d';
        removeBtn.style.color = 'white';
        removeBtn.style.border = 'none';
        removeBtn.style.cursor = 'pointer';
        removeBtn.style.zIndex = '20';

        removeBtn.onmousedown = (e) => e.stopPropagation();

        function publish_schema(){
            fetch('/api/grade_schema', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(root_data)
            });
        };

        removeBtn.onclick = async () => {
            if (confirm(`Are you sure you want to delete "${node[0]}" and all its children?`)) {
                
                const removeNodeRecursive = (parent) => {
                    if (!parent[2]) return;
                    const index = parent[2].indexOf(node);
                    if (index > -1) {
                        parent[2].splice(index, 1);
                        return true;
                    }
                    for (let child of parent[2]) {
                        if (removeNodeRecursive(child)) return true;
                    }
                    return false;
                };

                removeNodeRecursive(root_data);

                publish_schema();

                load_course_editor();
            }
        };

         box.innerHTML = `
            <div style="display: flex; flex-direction: column; gap: 8px;">
                <input type="text" class="edit-name" 
                    style="font-size: 14px; font-weight: bold; width: 100%; border: none; border-bottom: 1px solid #ccc; background: transparent;" 
                    value="${name}" placeholder="Assessment">
                
                <div style="display: flex; flex-direction: column; gap: 6px;">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <span style="font-size: 11px; color: #555;">Max Points:</span>
                        <input type="number" class="edit-max-pts" 
                            style="font-size: 12px; width: 50px; border: 1px solid #ddd; border-radius: 3px; padding: 2px;" 
                            value="${node[1] || 0}">
                    </div>

                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <span style="font-size: 11px; color: #555;">Weight:</span>
                        <div style="display: flex; align-items: center;">
                            <input type="number" class="edit-weight-pct" 
                                style="font-size: 12px; width: 50px; border: 1px solid #ddd; border-radius: 3px; padding: 2px;" 
                                value="${node[4] || 0}">
                            <span style="font-size: 12px; font-weight: bold; margin-left: 3px;">%</span>
                        </div>
                    </div>
                </div>
            </div>
        `;

        const nameInp = box.querySelector('.edit-name');
        const maxPtsInp = box.querySelector('.edit-max-pts');
        const weightPctInp = box.querySelector('.edit-weight-pct');

        nameInp.onchange = (e) => { 
            node[0] = e.target.value;
            publish_schema();
        };

        maxPtsInp.onchange = (e) => { 
            node[1] = parseFloat(e.target.value) || 0; 
            publish_schema();
        };

        weightPctInp.onchange = (e) => { 
            node[4] = parseFloat(e.target.value) || 0;
            publish_schema();
        };

        [nameInp, maxPtsInp, weightPctInp].forEach(el => {
            el.onmousedown = (e) => e.stopPropagation();
        });

        wrapper.appendChild(removeBtn);
    } else{
        box.innerHTML = `
            <input type="text" class="edit-name" style="font-size: 14px; font-weight: bold; width: 100%; border: none; background: transparent;" value="${name}">
            <input type="text" class="edit-type" style="font-size: 12px; color: #666; width: 100%; border: none; background: transparent;" value="Total Pts"">
            <div style="display: flex; align-items: center; margin-top: 5px;">
                <input type="number" class="edit-weight" style="font-size: 12px; font-weight: bold; width: 50px; border: 1px solid #ddd;" value="${weightage}">
                <span style="font-size: 12px; font-weight: bold;">%</span>
            </div>
        `;
    }
    
    wrapper.appendChild(box);
    wrapper.appendChild(actionBtn);
    container.appendChild(wrapper);

    if (children && children.length > 0) {
        children.forEach(child => {
            render_node(child, container, root_data);
        });
    }
};

async function load_course_editor(){
    const frame = document.getElementById("course-scheme-editor");
    frame.classList.remove("hidden");
    const schema_container = document.getElementById("editor-container");

    const response = await fetch('/api/select_course');
    const data = await response.json();

    const course_editing = data.course_editing;
    const course_editing_id = data.course_editing_id;
    const course_title_header = document.getElementById("course-title");

    if (course_editing !== "NONE") {
        course_title_header.textContent = `Currently editing course: ${course_editing} | ID: ${course_editing_id}`;
    } else {
        course_title_header.textContent = "No course selected";
        return;
    }
    const grade_schema_info = await fetch('/api/grade_schema');
    const grade_schema_info_data = await grade_schema_info.json();
    schema_container.innerHTML = '';

    schema_container.innerHTML = '<svg id="svg-canvas" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;"></svg>'; 

    render_node(grade_schema_info_data, schema_container, grade_schema_info_data);
    drawAllStems(grade_schema_info_data);
}

function route(){
    const path = decodeURIComponent(window.location.pathname);
    const course_select_frame = document.getElementById("course-selector");
    const grade_frame = document.getElementById("student-grades");
    const course_editor_frame = document.getElementById("course-scheme-editor");

    course_select_frame.classList.add("hidden");
    grade_frame.classList.add("hidden");
    course_editor_frame.classList.add("hidden");

    if (path.includes("/main/Class&20Selector")){
        course_select_frame.classList.remove("hidden");
        if (document.getElementById("visual-course-box").children.length <= 2) {
            load_courses();
        }
    } else if (path.includes("Student Grade Spreadsheet Viewer")){
        grade_frame.classList.remove("hidden");
        load_grades();
    } else if (path.includes("Grading Schema Editor")){
        course_editor_frame.classList.remove("hidden");
        load_course_editor();
    }
}

document.addEventListener("click", (e) => {
    const link = e.target.closest(".link-button");

    if(link){
        e.preventDefault();
        const Tpath = e.target.getAttribute("d-path");
        window.history.pushState({}, "", Tpath);
        route();
    }
});

window.addEventListener("DOMContentLoaded", route);

async function load_grades(){
    const frame = document.getElementById("student-grades");
    frame.classList.remove("hidden");

    const response = await fetch('/api/grades');
    const users = await response.json();

    frame.innerHTML = "";

    const table = document.createElement("table");

    const header =`
        <tr>
            <th>Student ID </th>
            <th>Email</th>
            <th>First Name</th>
            <th>Last Name</th>
            <th>Section</th>
            <th>RM</th>
            <th>ERD</th>
            <th>RA</th>
            <th>SQL_DDL</th>
            <th>SQL_Base</th>
            <th>SQL_Adv</th>
            <th>HTML</th>
            <th>CSS</th>
            <th>Final Grade</th>
        </tr>
    `;
    table.innerHTML = header;

    users.forEach(user =>{
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${user.student_id}</td>
            <td>${user.email}</td>
            <td>${user.first_name}</td>
            <td>${user.last_name}</td>
            <td>${user.section}</td>
            <td>${user.RM}</td>
            <td>${user.ERD}</td>
            <td>${user.RA}</td>
            <td>${user.SQL_DDL}</td>
            <td>${user.SQL_Base}</td>
            <td>${user.SQL_Adv}</td>
            <td>${user.HTML}</td>
            <td>${user.CSS}</td>
            <td>${user.final_grade}</td> 
        `;
        table.appendChild(row);
    });

    frame.appendChild(table);
}

document.addEventListener("DOMContentLoaded", () => {
    window.history.pushState({}, "", "/main/Class&20Selector");

    const course_select_frame = document.getElementById("course-selector");
    const path = decodeURIComponent(window.location.pathname);
    if (path.includes("/main/Class&20Selector")){
        course_select_frame.classList.add("hidden");
    } else{
        load_courses();
    }
});

// need to put users into the table