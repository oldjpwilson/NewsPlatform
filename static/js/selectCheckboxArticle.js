const LATEST_ID = "id_latest";
const VIEW_COUNT_ID = "id_view_count";
const RATING_ID = "id_rating";

const latest = document.getElementById(LATEST_ID);
const view_count = document.getElementById(VIEW_COUNT_ID);
const rating = document.getElementById(RATING_ID);

function switchEnabled(formElement) {
  const checked = formElement.checked;
  if (checked) formElement.checked = false;
}

latest.addEventListener("change", e => {
  switchEnabled(view_count);
  switchEnabled(rating);
});

view_count.addEventListener("change", e => {
  switchEnabled(latest);
  switchEnabled(rating);
});

rating.addEventListener("change", e => {
  switchEnabled(latest);
  switchEnabled(view_count);
});
