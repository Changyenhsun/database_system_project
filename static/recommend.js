document.addEventListener("DOMContentLoaded", () => {
    const checkboxes = document.querySelectorAll('.drama-checkbox');

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            const title = checkbox.dataset.title;
            const genre = checkbox.dataset.genre;

            let list = JSON.parse(localStorage.getItem('myList')) || [];

            if (checkbox.checked) {
                list.push({ title, genre });
            } else {
                list = list.filter(item => item.title !== title);
            }

            localStorage.setItem('myList', JSON.stringify(list));
        });
    });
});

function showMyList() {
    const list = JSON.parse(localStorage.getItem('myList')) || [];
    if (list.length === 0) {
        alert("你的清單是空的喔！");
    } else {
        const message = list.map(item => `${item.title}（${item.genre}）`).join('\n');
        alert("你的清單：\n\n" + message);
    }
}
