import { Peer } from "https://cdn.webrtc.ecl.ntt.com/skyway-latest.js";

const localVideo = document.getElementById("local-video");
const videoContainer = document.getElementById("video-container");
const roomNameInput = document.getElementById("room-name");
const joinButton = document.getElementById("join");
const leaveButton = document.getElementById("leave");
const heartEffect = document.querySelector(".heart");
const ctx = document.getElementById("syncChart").getContext("2d");

const peer = new Peer({ key: "18e272cc-ffe1-4fc8-a309-55fa325cf15d" });

peer.on("open", (id) => {
    document.getElementById("my-id").textContent = id;
});

let room;

joinButton.addEventListener("click", () => {
    if (!roomNameInput.value) return alert("ルーム名を入力してください！");
    room = peer.joinRoom(roomNameInput.value, { mode: "mesh", stream: localVideo.srcObject });

    room.on("stream", (stream) => {
        const video = document.createElement("video");
        video.srcObject = stream;
        video.autoplay = true;
        video.playsInline = true;
        videoContainer.appendChild(video);
    });

    room.on("data", (message) => {
        if (message.data.type === "heartbeat") {
            updateHeartSync(message.data.value);
        }
    });

    navigator.mediaDevices.getUserMedia({ video: true, audio: true })
        .then((stream) => {
            localVideo.srcObject = stream;
            room.replaceStream(stream);
        })
        .catch((error) => console.error("MediaStreamエラー:", error));
});

leaveButton.addEventListener("click", () => {
    if (room) {
        room.close();
        videoContainer.innerHTML = '<video id="local-video" muted autoplay playsinline></video>';
    }
});

// 心拍同期データの送信
setInterval(() => {
    if (room) {
        const heartbeatValue = Math.random(); // 仮のデータ（本物の心拍数を取得する場合はここを変更）
        room.send({ type: "heartbeat", value: heartbeatValue });
    }
}, 1000);

// ハートエフェクト & グラフ更新
const heartRateData = [];
const timeLabels = [];
const maxDataPoints = 20;

const syncChart = new Chart(ctx, {
    type: "line",
    data: {
        labels: timeLabels,
        datasets: [{
            label: "Heart Sync %",
            data: heartRateData,
            borderColor: "red",
            borderWidth: 2,
            fill: false,
        }]
    },
    options: {
        responsive: true,
        scales: {
            x: { display: false },
            y: { min: 0, max: 1 }
        }
    }
});

function updateHeartSync(value) {
    heartRateData.push(value);
    timeLabels.push("");
    if (heartRateData.length > maxDataPoints) {
        heartRateData.shift();
        timeLabels.shift();
    }
    syncChart.update();

    if (value > 0.5) {
        heartEffect.style.animation = "beat 0.5s infinite";
    } else {
        heartEffect.style.animation = "none";
    }
}
