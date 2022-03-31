%%
%%
fs = 2.5e6;
fc = 5000;
fpass = (fc/(fs/2))/2;
fstop = (fc/(fs/2))*2;

%%
om=pi*[linspace(0,fpass,20),linspace(fstop,1,60)]; % frequency vector
D=[exp(-j*om(1:20)*5),zeros(1,60)]; % desired complex frequency response
W=ones(1,80); % unity weighting
[b,a,e] = mpiir_l2(15,15,om,D,W,.99); % least squares design

%%
function [b,a,l2error] = mpiir_l2(M,N,om,D,W,r,a0)
% MPIIR_L2: [b,a,l2error] = mpiir_l2(M,N,om,D,W,r,a0)
% Least Squares Digital IIR Filter Design with Arbitrary Magnitude
% and Phase Responses and Specified Maximum Pole Radius
%
% OUTPUT:
% b numerator polynomial coefficients
% a denominator polynomial coefficients
% l2error approximation error
%
% INPUT:
% M order of numerator polynomial
% N order of denominator polynomial
% om frequency grid, 0<=om<=pi
% D complex desired frequency response on the grid om
% W positive weighting function on the grid om
% r maximum pole radius
% a0 initial denominator guess; optional
%
% EXAMPLE:
% Lowpass filter with approximately linear passband phase
% (passband group delay = 19 samples, maximum pole radius = 0.97)
% om=pi*[linspace(0,.2,20),linspace(.25,1,75)];
% D=[exp(-j*om(1:20)*19),zeros(1,75)];
% W=[ones(1,20),100*ones(1,75)];
% [b,a,e]=mpiir_l2(16,6,om,D,W,.97);
%
% Author: Mathias C. Lang, Vienna University of Technology, Oct. 98
om=om(:); D=D(:); W=W(:); srW = sqrt(W);
EM = exp(-j*om*(0:max([M,N]))); tol = 1e-4; alpha = 0.5;
disp(' ERROR MAX.RADIUS STEP SLOPE');
% initial solution
ini=0;
if nargin == 7,
a=a0(:);
if length(a)~=N+1, ini=1;
elseif a(1)==0, ini=1;
elseif max(abs(roots(a))) > r, ini=1;
else
if a(1)~=1, a=a/a(1); end
A = freqz(a,1,om); b = lslevin(M+1,om,A.*D,W./(abs(A).^2));
end
else, ini=1;
end
if ini, % compute FIR solution
a = [1;zeros(N,1)]; b = lslevin(M+1,om,D,W);
end
x = [a(2:N+1);b]; delta = [];
% iterate (outer loop)
while 1,
% compute complex error, Jacobian, and objective function value
A = EM(:,1:N+1)*a; B = EM(:,1:M+1)*b; H = B./A;
E = srW.*(D - H); l2error = E'*E; if N<1, break; end
vec1 = srW./A; vec2 = -vec1.*H;
J = [vec2(:,ones(1,N)).*EM(:,2:N+1),vec1(:,ones(1,M+1)).*EM(:,1:M+1)];
% compute search direction
delta0 = delta;
[delta,how] = update(J,E,a,r,M,N);
if ~strcmp(how,'ok'), delta=delta0; break; end
% update solution
x = x + alpha*delta; a = [1;x(1:N)]; b = x(N+1:M+N+1);
% display results
step = norm(delta)/norm(x); pr = max(abs(roots(a)));
slope = -2*real(E'*J)*delta/l2error;
disp(sprintf('\b \b %5.3e %5.3e %5.3e %5.3e',l2error,pr,step,slope))
% check stopping criterion
if (step < tol & abs(slope) < tol) | pr > r, break; end
end % outer loop
end
%%
function [delta,how] = update(J,E,a,r,M,N)
% subroutine for mpiir_l2.m (IIR filter design)
% computes solution update subject to constraint on pole radii;
% applies Rouche's Theorem
% J Jacobian of actual frequency response
% E complex error
% a actual denominator coefficients
% r maximum pole radius
% M order of numerator polynomial
% N order of denominator polynomial
%
% Author: Mathias C. Lang, Vienna University of Technology, Oct. 98
tol = 1e-6; se = sqrt(eps); itmax = 10; cnt = 0; how = 'ok';
nfft = 2^10; om = 2*pi*(0:nfft/2)'/nfft;
a = a.*(r.^-(0:N)'); A = abs(fft(a,nfft)); A = A(1:nfft/2+1); A=A(:);
ra = conv(a,a(N+1:-1:1)); ra = ra(N+1:2*N+1);
nra = (1:N)'.*ra(2:N+1); n2ra = (1:N)'.*nra;
R = r.^-(1:N); Bact=[]; cact=[];
% solve unconstrained problem
J = [real(J);imag(J)]; E = [real(E);imag(E)];
H=J'*J; H=H+se*eye(size(H)); f=J'*E; delta=H\f;
% compute matrices and vectors for qp-subproblems
H11=H(1:N,1:N); H12=H(1:N,N+1:M+N+1); H22=H(N+1:M+N+1,N+1:M+N+1);
Hh=H12/H22; H=H11-Hh*H12'; H=.5*(H+H');
f1=f(1:N); f2=f(N+1:M+N+1); f=Hh*f2-f1;
% iterate
while cnt<50,
% compute error maxima on a grid
d = delta(1:N); d = d.*(r.^-(1:N)');
D = abs(fft(d,nfft)); D = D(1:nfft/2+1); D=D(:);
Imax = locmax(D.^2-A.^2); ommax = om(Imax);
if ~length(Imax), break; end
% refine maxima using Newton's method
if N>1,
rd = conv(d,d(N:-1:1)); rd = rd(N:2*N-1);
nrd = (1:N-1)'.*rd(2:N); n2rd = (1:N-1)'.*nrd;
end
for i=1:itmax,
Mc = cos(ommax*(1:N)); Ms = sin(ommax*(1:N));
gp = -Ms*nra; gpp = -Mc*n2ra;
if N>1, gp = gp + Ms(:,1:N-1)*nrd; gpp = gpp + Mc(:,1:N-1)*n2rd; end
Ipp = find(gpp); if ~length(Ipp), break; end
ommax(Ipp) = ommax(Ipp)- gp(Ipp)./gpp(Ipp);
end
% find violating maxima
Dmax = exp(-j*ommax*(1:N))*d; Amax = exp(-j*ommax*(0:N))*a;
Iviol = find(abs(Dmax)>abs(Amax));
omviol = ommax(Iviol); nviol = length(Iviol);
Dviol = Dmax(Iviol); Aviol = Amax(Iviol);
% check stopping criterion
if ~nviol | all(abs(Dmax)-abs(Amax)<=max(abs(Amax)*tol,se)), break; end
cnt = cnt+1;
% formulate new constraints
PDviol = angle(Dviol);
B = R(ones(nviol,1),:).*cos(omviol*(1:N)+PDviol(:,ones(N,1)));
c = abs(Aviol);
% solve subproblem
B=[Bact;B]; c=[cact;c];
%[delta,lam,how]=qp(H,f,B,c);
[delta,lam,how]=quadprog(H,f,B,c);
if ~strcmp(how,'ok'), break; end
% find active constraints
act = find(lam>0); Bact = B(act,:); cact = c(act);
end
% add numerator coefficient update
if length(delta)==N, delta=[delta;H22\f2-Hh'*delta]; end
end
%%
function h = lslevin(N,om,D,W)
% h = lslevin(N,om,D,W)
% Complex Least Squares FIR filter design using Levinson's algorithm
%
% h filter impulse response
% N filter length
% om frequency grid (0 <= om <= pi)
% D complex desired frequency response on the grid om
% W positive weighting function on the grid om
%
% example: length 61 bandpass, band edges [.23,.3,.5,.57]*pi,
% weighting 1 in passband and 10 in stopbands, desired passband
% group delay 20 samples
%
% om=pi*[linspace(0,.23,230),linspace(.3,.5,200),linspace(.57,1,430)];
% D=[zeros(1,230),exp(-j*om(231:430)*20),zeros(1,430)];
% W=[10*ones(1,230),ones(1,200),10*ones(1,430)];
% h = lslevin(61,om,D,W);
%
% Author: Mathias C. Lang, Vienna University of Technology, July 1998
om = om(:); D = D(:); W = W(:); L = length(om);
DR = real(D); DI = imag(D); a = zeros(N,1); b = a;
% Set up vectors for quadratic objective function
% (avoid building matrices)
dvec = D; evec = ones(L,1); e1 = exp(j*om);
for i=1:N,
a(i) = W.'*real(evec);
b(i) = W.'*real(dvec);
evec = evec.*e1; dvec = dvec.*e1;
end
a=a/L; b=b/L;
% Compute weighted l2 solution
h = levin(a,b);
end
%%

function x = levin(a,b)
% function x = levin(a,b)
% solves system of complex linear equations toeplitz(a)*x=b
% using Levinson's algorithm
% a ... first row of positive definite Hermitian Toeplitz matrix
% b ... right hand side vector
%
% Author: Mathias C. Lang, Vienna University of Technology, AUSTRIA
% 9-97
a = a(:); b = b(:); n = length(a);
t = 1; alpha = a(1); x = b(1)/a(1);
for i = 1:n-1,
k = -(a(i+1:-1:2)'*t)/alpha;
t = [t;0] + k*flipud([conj(t);0]);
alpha = alpha*(1 - abs(k)^2);
k = (b(i+1) - a(i+1:-1:2)'*x)/alpha;
x = [x;0] + k*flipud(conj(t));
end
end
%%
function I = locmax(x)
% LOCMAX: I = locmax(x)
% finds indices of local maxima of data x
x = x(:); n = length(x);
if n, I = find(x > [x(1)*(1-eps)-1;x(1:n-1)] & ...
x > [x(2:n);x(n)*(1-eps)-1]);
else, I = []; end
end