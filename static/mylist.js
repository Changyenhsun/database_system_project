document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("list-items");
    const clearBtn = document.getElementById("clear-list-btn");

    function loadList() {
        container.innerHTML = "";
        const list = JSON.parse(localStorage.getItem("myList")) || [];

        if (list.length === 0) {
            container.innerHTML = "<li>你還沒有選取任何電影。</li>";
            return;
        }

        list.forEach((item, index) => {
            const li = document.createElement("li");
            li.textContent = `${item.title}（${item.genre}）`;

            const removeBtn = document.createElement("button");
            removeBtn.textContent = "❌";
            removeBtn.classList.add("remove-btn");
            removeBtn.onclick = () => {
                removeItem(index);
            };

            li.appendChild(removeBtn);
            container.appendChild(li);
        });
    }

    function removeItem(index) {
        let list = JSON.parse(localStorage.getItem("myList")) || [];
        list.splice(index, 1);
        localStorage.setItem("myList", JSON.stringify(list));
        loadList(); // 重新渲染
    }

    clearBtn.addEventListener("click", () => {
        if (confirm("確定要清空整份清單嗎？")) {
            localStorage.removeItem("myList");
            loadList();
        }
    });

    loadList();
});
