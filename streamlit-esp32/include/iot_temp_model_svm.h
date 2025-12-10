#pragma once
#include <cstdarg>
namespace Eloquent {
    namespace ML {
        namespace Port {
            class SVM {
                public:
                    /**
                    * Predict class for features vector
                    */
                    int predict(float *x) {
                        float kernels[8] = { 0 };
                        float decisions[3] = { 0 };
                        int votes[3] = { 0 };
                        kernels[0] = compute_kernel(x,   23.9  , 60.5 );
                        kernels[1] = compute_kernel(x,   23.9  , 59.8 );
                        kernels[2] = compute_kernel(x,   23.6  , 61.5 );
                        kernels[3] = compute_kernel(x,   28.8  , 68.8 );
                        kernels[4] = compute_kernel(x,   31.9  , 60.3 );
                        kernels[5] = compute_kernel(x,   31.9  , 60.9 );
                        kernels[6] = compute_kernel(x,   31.9  , 62.1 );
                        kernels[7] = compute_kernel(x,   32.0  , 68.6 );
                        decisions[0] = 15.232993298172
                        + kernels[2] * 0.024897226002
                        + kernels[3] * -0.024897226002
                        ;
                        decisions[1] = 6.976769877513
                        + kernels[0] * 0.031179946754
                        + kernels[1] * 6.9879984e-05
                        + kernels[4] * -0.026230344055
                        + kernels[5] * -0.00233690662
                        + kernels[6] * -0.002682576063
                        ;
                        decisions[2] = 16.252479969287
                        + kernels[3] * 0.194547191403
                        + kernels[7] * -0.194547191403
                        ;
                        votes[decisions[0] > 0 ? 0 : 1] += 1;
                        votes[decisions[1] > 0 ? 0 : 2] += 1;
                        votes[decisions[2] > 0 ? 1 : 2] += 1;
                        int val = votes[0];
                        int idx = 0;

                        for (int i = 1; i < 3; i++) {
                            if (votes[i] > val) {
                                val = votes[i];
                                idx = i;
                            }
                        }

                        return idx;
                    }

                protected:
                    /**
                    * Compute kernel between feature vector and support vector.
                    * Kernel type: linear
                    */
                    float compute_kernel(float *x, ...) {
                        va_list w;
                        va_start(w, 2);
                        float kernel = 0.0;

                        for (uint16_t i = 0; i < 2; i++) {
                            kernel += x[i] * va_arg(w, double);
                        }

                        return kernel;
                    }
                };
            }
        }
    }