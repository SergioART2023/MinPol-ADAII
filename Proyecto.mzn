int: n;
int: m;
set of int: OP = 1..m;
int: half = n div 2;

array[OP] of int: p;
array[OP] of float: v;
array[OP] of float: ce;
array[OP, OP] of float: c;
float: ct;
int: maxM;

array[OP, OP] of var 0..n: x;
array[OP] of var 0..n: y;
array[OP] of var 0..1: z;
array[OP, OP] of var 0..n: u;

array[OP, OP] of float: unit_cost = array2d(
  OP,
  OP,
  [
    if i = j then 0.0
    else
      c[i, j] * (1.0 + int2float(p[i]) / int2float(n)) +
      (if p[j] = 0 then ce[j] else 0.0 endif)
    endif
    | i in OP, j in OP
  ]
);

array[OP, OP] of int: unit_movements = array2d(
  OP,
  OP,
  [abs(i - j) | i in OP, j in OP]
);

array[OP, OP] of float: deviation = array2d(
  OP,
  OP,
  [abs(v[j] - v[k]) | k in OP, j in OP]
);

constraint forall(i in OP)(sum(j in OP)(x[i, j]) = p[i]);
constraint forall(j in OP)(y[j] = sum(i in OP)(x[i, j]));
constraint sum(k in OP)(z[k]) = 1;

constraint forall(k in OP)(
  sum(j in 1..k - 1)(y[j]) <= half + n * (1 - z[k]) /\
  sum(j in k + 1..m)(y[j]) <= half + n * (1 - z[k])
);

constraint forall(j in OP)(sum(k in OP)(u[k, j]) = y[j]);
constraint forall(k in OP, j in OP)(
  u[k, j] <= y[j] /\
  u[k, j] <= n * z[k] /\
  u[k, j] >= y[j] - n * (1 - z[k])
);

var float: total_cost = sum(i in OP, j in OP)(unit_cost[i, j] * int2float(x[i, j]));
var int: total_movements = sum(i in OP, j in OP)(unit_movements[i, j] * x[i, j]);
var float: total_polarization = sum(k in OP, j in OP)(deviation[k, j] * int2float(u[k, j]));
var int: median_index = sum(k in OP)(k * z[k]);

constraint total_cost <= ct;
constraint total_movements <= maxM;

solve minimize total_polarization;

output [
  "polarizacion=" ++ show(total_polarization) ++ "\n" ++
  "costo_total=" ++ show(total_cost) ++ "\n" ++
  "movimientos_totales=" ++ show(total_movements) ++ "\n" ++
  "indice_mediana=" ++ show(median_index) ++ "\n" ++
  "distribucion_final=" ++ show([y[j] | j in OP]) ++ "\n" ++
  concat(["fila_" ++ show(i) ++ "=" ++ show([x[i, j] | j in OP]) ++ "\n" | i in OP])
];
