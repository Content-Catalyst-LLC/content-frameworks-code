program value_relevance_score
  implicit none
  real :: score
  score = (0.91 + 0.84 + 0.86 + 0.76 + 0.90 + 0.88) / 6.0
  print '(A,F5.3)', 'Value relevance score: ', score
end program value_relevance_score
