document.addEventListener("DOMContentLoaded", () => {
    const checkboxes = document.querySelectorAll('.drama-checkbox');

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            const title = checkbox.dataset.title;
            const genre = checkbox.dataset.genre || '未分類';

            let list = JSON.parse(localStorage.getItem('myList')) || [];

            if (checkbox.checked) {
                // 避免重複加入相同戲劇
                if (!list.some(item => item.title === title)) {
                    list.push({ title, genre });
                }
            } else {
                list = list.filter(item => item.title !== title);
            }

            localStorage.setItem('myList', JSON.stringify(list));
            console.log("新增清單項目：", { title, genre });

        });
    });
});

function showMyList() {
    const list = JSON.parse(localStorage.getItem('myList')) || [];
    if (list.length === 0) {
        alert("你的清單是空的喔！");
    } else {
        const message = list.map(item => {
            const genreText = item.genre && item.genre !== '未分類' ? `（${item.genre}）` : '';
            return `${item.title}${genreText}`;
        }).join('\n');

        alert("你的清單：\n\n" + message);
    }
}
