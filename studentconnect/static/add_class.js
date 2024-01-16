function blockCheck(value) {
    const blocks = ["D", "E"];
    if (blocks.includes(value)) {
        for (const element of document.getElementsByClassName("single_lesson")) {
            element.style.display = "inline";
        }
    } else {
        for (const element of document.getElementsByClassName("single_lesson")) {
            element.style.display = "none";
        }
    }
}

function guidanceCheck(value) {
    if (value == "1") {
        for (const element of document.getElementsByClassName("block")) {
            element.style.display = "none";
        }
        for (const element of document.getElementsByClassName("single_lesson")) {
            element.style.display = "inline";
        }
    } else {
        for (const element of document.getElementsByClassName("block")) {
            element.style.display = "inline";
        }
        for (const element of document.getElementsByClassName("single_lesson")) {
            element.style.display = "none";
        }
    }   
}

blockCheck(document.getElementById("block").value);
guidanceCheck(document.getElementById("subject").value);