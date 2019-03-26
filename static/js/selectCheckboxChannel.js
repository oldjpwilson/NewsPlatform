const LATEST_ID = "id_latest";
const VIEW_COUNT_ID = "id_view_count";
const RATING_ID = "id_rating";
const SUB_COUNT_ID = "id_sub_count";

const latest = document.getElementById(LATEST_ID);
const view_count = document.getElementById(VIEW_COUNT_ID);
const rating = document.getElementById(RATING_ID);
const sub_count = document.getElementById(SUB_COUNT_ID);

function switchEnabled(formElement) {
  const checked = formElement.checked;
  if (checked) formElement.checked = false;
}

latest.addEventListener("change", e => {
  switchEnabled(view_count);
  switchEnabled(rating);
  switchEnabled(sub_count);
});

view_count.addEventListener("change", e => {
  switchEnabled(latest);
  switchEnabled(rating);
  switchEnabled(sub_count);
});

rating.addEventListener("change", e => {
  switchEnabled(latest);
  switchEnabled(view_count);
  switchEnabled(sub_count);
});

sub_count.addEventListener("change", e => {
  switchEnabled(latest);
  switchEnabled(view_count);
  switchEnabled(rating);
});
