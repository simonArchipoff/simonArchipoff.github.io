#include <iostream>
#include <chrono>
#include <fftw3.h>
#include <cassert>
#define WISDOM "/home/simon/.config/fftw_wisdome"




int main(int argc, char * argv[]) {
  assert(argc > 1);
  const int size = atoi(argv[1]);
  auto err = fftw_import_wisdom_from_filename(WISDOM);


  int align = 0;
  const char * align_str=std::getenv("FFT_ALIGN");
  if(align_str)
    align=atoi(align_str);
  
  fftw_complex *in = (fftw_complex*)fftw_malloc(sizeof(fftw_complex) * size + align);
  fftw_complex *out = (fftw_complex*)fftw_malloc(sizeof(fftw_complex) * size + align);
  

  auto p = fftw_plan_dft_1d(size, (fftw_complex*)(((char*)in)+align) ,(fftw_complex*)(((char*) out) + align), FFTW_FORWARD, FFTW_DESTROY_INPUT | FFTW_PATIENT | (align ? FFTW_UNALIGNED : 0));



  fftw_fprint_plan(p,stderr);
  
    // Afficher le coût estimé de la transformation FFT
    fprintf(stderr, "\nCoût estimé : %lf\n", fftw_cost(p));

    // Variables pour stocker le coût en flops
    double add, mul, fma;

    // Obtenir le coût en flops
    fftw_flops(p, &add, &mul, &fma);

    // Afficher le coût en flops
    fprintf(stderr, "Coût en flops (add, mul, fma) : %lf, %lf, %lf\n", add, mul, fma);

  
  for(int j = 0; j < 10000 ; j++){
    for(int i = 0; i < size; i++){
      in[i][0] = rand();
      in[i][1] = rand();
    }

    auto start = std::chrono::high_resolution_clock::now();
    fftw_execute(p);
    auto end = std::chrono::high_resolution_clock::now();
    auto time_span = std::chrono::duration_cast<std::chrono::duration<int64_t,std::nano>>(end - start);
  
    printf("%d;%ld\n",size,time_span.count());
  }

  fftw_export_wisdom_to_filename(WISDOM);    

  return 0;
}

