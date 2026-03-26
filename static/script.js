async function load_courses(){
    // remove hidden from course frame
    // or this will not work
    const course_parent = document.getElementById("course-selector");
    course_parent.classList.remove("hidden");
    const frame = document.getElementById("visual-course-box");

    const response = await fetch('/api/courses');
    const courses = await response.json();

    frame.innerHTML = '<div class="course-title">Your courses</div>';

    courses.forEach(course => {
            const btn = document.createElement('button');
            btn.className = 'course-button';
            btn.textContent = `${course.code} : ${course.name}`;
            frame.appendChild(btn);

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
                    body: JSON.stringify({ course_code: course.code.trim() })
                });

                const text = await response.text();
                const result = JSON.parse(text);

                if (result[0] === "Successful course removal") {
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

        const response = await fetch('/api/add_course', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ course_code: add_input.value.trim() })
        });

        const text = await response.text();
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

function route(){
    path = decodeURIComponent(window.location.pathname);
    frame = document.getElementById("course-selector");

    if (path.includes("/main/Class&20Selector")){
        load_courses();
    } else{
        frame.classList.add("hidden");
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

// need to put users into the table