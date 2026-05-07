const BOOK_COVERS = [
  "https://images.unsplash.com/photo-1512820790803-83ca734da794d?auto=format&fit=crop&w=520&q=80",
  "https://images.unsplash.com/photo-1495446815901-a7297e633e8d?auto=format&fit=crop&w=520&q=80",
  "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?auto=format&fit=crop&w=520&q=80",
  "https://images.unsplash.com/photo-1516979187457-637abb4f9353?auto=format&fit=crop&w=520&q=80",
  "https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=520&q=80",
  "https://images.unsplash.com/photo-1507842217343-583bb7270b66?auto=format&fit=crop&w=520&q=80",
];

const AVATARS = [
  "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=220&q=80",
  "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=220&q=80",
  "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=220&q=80",
  "https://images.unsplash.com/photo-1519345182560-3f2917c472ef?auto=format&fit=crop&w=220&q=80",
  "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=220&q=80",
  "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=220&q=80",
];

function hashSeed(value) {
  const text = String(value || "bookcircle");
  let hash = 0;
  for (let i = 0; i < text.length; i += 1) {
    hash = (hash * 31 + text.charCodeAt(i)) >>> 0;
  }
  return hash;
}

function pick(list, seed) {
  return list[hashSeed(seed) % list.length];
}

export function bookCover(book) {
  return book?.cover_url || pick(BOOK_COVERS, book?.id || book?.title);
}

export function userAvatar(user) {
  return user?.avatar_url || pick(AVATARS, user?.id || user?.username);
}

export function coverStyle(book) {
  return {
    backgroundImage: `
      linear-gradient(180deg, rgba(15,23,42,0.04), rgba(15,23,42,0.70)),
      url("${bookCover(book)}")
    `,
  };
}
