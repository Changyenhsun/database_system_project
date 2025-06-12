document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("my-list-container");
    const list = JSON.parse(localStorage.getItem("myList")) || [];

    if (list.length === 0) {
        container.innerHTML = "<p>你還沒有選取任何電影。</p>";
    } else {
        const ul = document.createElement("ul");

        list.forEach(item => {
            const li = document.createElement("li");
            li.textContent = `${item.title}（${item.genre}）`;
            ul.appendChild(li);
        });

        container.appendChild(ul);
    }
});
