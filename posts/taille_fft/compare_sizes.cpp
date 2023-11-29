#include <iostream>
#include <chrono>
#include <fftw3.h>
#include <cassert>
#define WISDOM "/home/simon/.config/fftw_wisdome"


struct result_bench{
  int size;
  int64_t mean_duration;
};

template<typename T>
bool no_stupid_factor(T n){
  auto good_factors = {2,3,5,7,11,13,17,19,23};
  for(const auto & factor : good_factors){
        while(n % factor == 0){
            n /= factor;
        }
    }
    return n == 1;
}

struct result_bench bench(int size){
  
  fftw_complex *in = (fftw_complex*)fftw_malloc(sizeof(fftw_complex) * size);
  fftw_complex *out = (fftw_complex*)fftw_malloc(sizeof(fftw_complex) * size);
  

  struct result_bench res;
  int nb_runs = 0;
  res.size = size;
  res.mean_duration = 0;

  auto p = fftw_plan_dft_1d(size, in ,out, FFTW_FORWARD, FFTW_DESTROY_INPUT | FFTW_MEASURE);

  while(res.mean_duration < 1000000 | nb_runs < 100){
  for(int i = 0; i < size; i++){
    in[i][0] = rand();
    in[i][1] = rand();
  }
  
    auto start = std::chrono::high_resolution_clock::now();
    fftw_execute(p);
    auto end = std::chrono::high_resolution_clock::now();
    auto time_span = std::chrono::duration_cast<std::chrono::duration<int64_t,std::nano>>(end - start);
    res.mean_duration += time_span.count();
    nb_runs++;
  }

  res.mean_duration /= nb_runs;
  
  fftw_free(in);
  fftw_free(out);
  fftw_destroy_plan(p);
  return res;
}

int save = 0;

int main(int argc, char * argv[]) {
  assert(argc > 1);
  const int minN = (1 << atoi(argv[1])) +1;
    const int maxN = 1<< (atoi(argv[1]) +1);
    auto err = fftw_import_wisdom_from_filename(WISDOM);
    printf("size;duration_ns\n");
    for (int n = minN; n <= maxN; n++) {
      if(1||no_stupid_factor(n)){	
	auto r = bench(n);
	printf("%d;%ld\n",r.size,r.mean_duration);
	fflush(stdout);
	if((save++) % 100 == 0)
	  fftw_export_wisdom_to_filename(WISDOM);    
      }
    }

    fftw_export_wisdom_to_filename(WISDOM);    

    return 0;
}
