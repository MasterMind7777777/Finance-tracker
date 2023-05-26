const stickyNotes = document.querySelectorAll('.sticky-note');

stickyNotes.forEach((note) => {
  note.addEventListener('dragstart', dragStart);
  note.addEventListener('dragend', dragEnd);
});

function dragStart(event) {
  event.dataTransfer.setData('text/plain', event.target.id);
  event.target.classList.add('dragging');
}

function dragEnd(event) {
  event.target.classList.remove('dragging');
}

const canvas = document.querySelector('.canvas');

canvas.addEventListener('dragover', dragOver);
canvas.addEventListener('drop', drop);

function dragOver(event) {
  event.preventDefault();
}

function drop(event) {
  event.preventDefault();
  const stickyNoteId = event.dataTransfer.getData('text/plain');
  const stickyNote = document.getElementById(stickyNoteId);
  const rect = canvas.getBoundingClientRect();
  const x = event.clientX - rect.left - stickyNote.offsetWidth / 2;
  const y = event.clientY - rect.top - stickyNote.offsetHeight / 2;
  stickyNote.style.left = `${x}px`;
  stickyNote.style.top = `${y}px`;
}
