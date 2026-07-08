// SSE 연결
const source = new EventSource("/event_log/stream_log");

console.log("logger_alarm.js 로드 완료");

window.addEventListener("load", function () {

    console.log("window.load 실행");

    console.log(
        "tbody =",
        document.getElementById("event_log_body")
    );

    console.log(
        "event_id =",
        document.querySelector(".event_id")
    );
});


// 알림음
const audio = new Audio("/static/audio/ding.wav");

// 마지막으로 받은 로그 ID
let lastLogId = null;


// 페이지 최초 로드
window.addEventListener("load", function() {

    const firstEventId = document.querySelector(".event_id");

    if(firstEventId) {
        lastLogId = firstEventId.innerText.trim();
    }

    console.log("초기 lastLogId =", lastLogId);
});


// SSE 수신
// source.onmessage = async function() {

//     console.log("새 로그 발생");

source.onmessage = async function(event){

    console.log("★★★★ SSE 수신 ★★★★");

    console.log(event.data);

    audio.play().catch(function(err) {
        console.log("알림음 재생 실패", err);
    });

    showToast("새 로그가 발생했습니다.");

    if(lastLogId === null){
        return;
    }

    // const response = await fetch(`/event_log/new?after=${lastLogId}`);

    // if (!response.ok) {
    //     return;
    // }

    // const logs = await response.json();
    // console.log("새 로그 =", logs);
    console.log("현재 lastLogId =", lastLogId);

    const response = await fetch(`/event_log/new?after=${lastLogId}`);

    console.log("response =", response);

    const logs = await response.json();

    console.log("받은 logs =", logs);

    logs.forEach(function(log) {

        console.log("추가할 로그 =", log);

        addLogRow(log);

        increaseBadge();
    });

    if(logs.length > 0) {
        lastLogId = logs[logs.length-1].ID;
    }
    console.log("새 lastLogId =", lastLogId);
};


// function addLogRow(log) {
//     const tbody = document.getElementById("event_log_body");

//     if(!tbody){
//         return;
//     }

//     const tr = document.createElement("tr");

//     tr.classList.add("new_log");

//     tr.innerHTML = `
//         <td>
//             <input class="log_check" type="checkbox" value="${log.ID}">
//         </td>
//         <td></td>

//         <td class="event_id">${log.ID}</td>
//         <td>${log.REG_DATE}</td>
//         <td>${log.latitude}</td>
//         <td>${log.longitude}</td>
//         <td>${log.TARGET_ID}</td>
//         <td>
//             <span class="unchecked">
//                 읽지 않음
//             </span>        
//         </td>
//     `;

//     tbody.prepend(tr);

//     refreshRowNumber();

//     setTimeout(function() {

//         tr.classList.remove("new_log");

//     }, 3000);
// }
function addLogRow(log) {

    console.log("addLogRow 실행");

    console.log(log);

    console.log("addLogRow 호출");

    const tbody = document.getElementById("event_log_body");

    console.log("tbody =", tbody);

    if (!tbody) {
        console.log("tbody 없음");
        return;
    }

    console.log("행 추가 시작");

    const tr = document.createElement("tr");

    tr.classList.add("new_log");

    tr.innerHTML = `
        <td>
            <input class="log_check" type="checkbox" value="${log.ID}">
        </td>
        <td></td>

        <td class="event_id">${log.ID}</td>
        <td>${log.REG_DATE}</td>
        <td>${log.latitude}</td>
        <td>${log.longitude}</td>
        <td>${log.TARGET_ID}</td>

        <td><span class="unchecked">읽지 않음</span></td>
    `;

    tbody.prepend(tr);

    console.log("행 추가 완료");

    refreshRowNumber();

    if (document.querySelector(`input[value="${log.ID}"]`)) {
        return;
    }
}

function showToast(text) {
    const container = document.getElementById("toast_container");

    if(!container) {
        return;
    }

    const div = document.createElement("div");

    div.className = "toast";

    div.innerText = text;

    container.appendChild(div);
    
    setTimeout(function() {

        div.remove();

    },3000);
}


function increaseBadge() {
    const badge = document.getElementById("log_badge");

    if(!badge)
        return;

    badge.innerText = Number(badge.innerText) + 1;
}