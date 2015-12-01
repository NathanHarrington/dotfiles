" print an iso timestamp
nnoremap <F5> m'A<C-R>="".strftime('%Y-%m-%d %H:%M')<CR>
map! <F5> <C-R>="".strftime('%Y-%m-%d %H:%M')<CR>

" Insert a random string suitable for password usage
nnoremap <F10> m'A<C-R>:r !pwgen 12 1 -s \| tr -d '\n'<CR>
map <F10> :r !pwgen 12 1 -s<CR>

set tw=72
set tabstop=4
set expandtab
set ignorecase
colors koehler

set nocursorline
" Use \c to show vertical alignment 
nnoremap <Leader>c :set cursorline! cursorcolumn!<CR>

" contrl lower case n to comment, upper case to uncomment
nnoremap  mn:s/^\(\s*\)*\(.*\)/\1#\2/ge:noh`n
vnoremap  mn:s/^\(\s*\)*\(.*\)/\1#\2/ge:nohgv`n
nnoremap t mn:s/^\(\s*\)#\([^ ]\)/\1\2/ge:s/^#$//ge:noh`n
vnoremap t mn:s/^\(\s*\)#\([^ ]\)/\1\2/gegv:s/#\n/\r/ge:nohgv`n

" alternative tab navigation
nnoremap th  :tabfirst<CR>
nnoremap tj  :tabnext<CR>
nnoremap tk  :tabprev<CR>
nnoremap tl  :tablast<CR>
nnoremap tt  :tabedit<Space>
nnoremap tn  :tabnext<Space>
nnoremap tm  :tabm<Space>
nnoremap td  :tabclose<CR>

