const ALPHABETICAL_ID = "id_alphabetical";
const ARTICLE_COUNT_ID = "id_article_count";
const RATING_ID = "id_rating";
const SUB_COUNT_ID = "id_sub_count";

const alphabetical = document.getElementById(ALPHABETICAL_ID);
const article_count = document.getElementById(ARTICLE_COUNT_ID);
const rating = document.getElementById(RATING_ID);
const sub_count = document.getElementById(SUB_COUNT_ID);

function switchEnabled(formElement) {
  const checked = formElement.checked;
  if (checked) formElement.checked = false;
}

alphabetical.addEventListener("change", e => {
  switchEnabled(article_count);
  switchEnabled(rating);
  switchEnabled(sub_count);
});

article_count.addEventListener("change", e => {
  switchEnabled(alphabetical);
  switchEnabled(rating);
  switchEnabled(sub_count);
});

rating.addEventListener("change", e => {
  switchEnabled(alphabetical);
  switchEnabled(article_count);
  switchEnabled(sub_count);
});

sub_count.addEventListener("change", e => {
  switchEnabled(alphabetical);
  switchEnabled(article_count);
  switchEnabled(rating);
});
