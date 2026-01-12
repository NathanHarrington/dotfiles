set ignorecase
set wrap linebreak
set guicursor=a:blinkon500-blinkoff500

let &t_SI = "\<Esc>[1 q"
let &t_EI = "\<Esc>[1 q"
let &t_SR = "\<Esc>[1 q"

augroup CursorBlink
  autocmd!
  autocmd VimLeave * silent! execute "normal! \e[1 q"
augroup END


set autowriteall
set autoread
augroup AutoRead
  autocmd!
  autocmd FocusGained,BufEnter,CursorHold,CursorHoldI * checktime
augroup END
set showtabline=2

" Tabline colors (black bar to the right)
highlight TabLineFill ctermfg=black ctermbg=black guifg=#000000 guibg=#000000
highlight TabLine ctermfg=34 ctermbg=black guifg=#008800 guibg=#000000
highlight TabLineSel ctermfg=green ctermbg=black guifg=#00ff00 guibg=#000000

autocmd ColorScheme * highlight TabLineFill ctermfg=black ctermbg=black guifg=#000000 guibg=#000000 | highlight TabLine ctermfg=34 ctermbg=black guifg=#008800 guibg=#000000 | highlight TabLineSel ctermfg=green ctermbg=black guifg=#00ff00 guibg=#000000
inoremap <C-S-k> <C-R>=strftime("%Y-%m-%d %H:%M")<CR> 
nnoremap <C-S-k> i<C-R>=strftime("%Y-%m-%d %H:%M")<CR> <Esc>
