%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                                                                          %
%          Generated by MATLAB 9.12 and Fixed-Point Designer 7.4           %
%                                                                          %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function out = observer_wrapper_fixpt(y1,y2,u,L,A,B)
    fm = get_fimath();
    y1_in = fi( y1, 1, 16, 0, fm );
    y2_in = fi( y2, 1, 16, 0, fm );
    u_in = fi( u, 1, 16, 0, fm );
    L_in = fi( L, 1, 16, 17, fm );
    A_in = fi( A, 1, 16, 3, fm );
    B_in = fi( B, 0, 16, 22, fm );
    [out_out] = observer_fixpt( y1_in, y2_in, u_in, L_in, A_in, B_in );
    out = double( out_out );
end

function fm = get_fimath()
	fm = fimath('RoundingMethod', 'Floor',...
	     'OverflowAction', 'Wrap',...
	     'ProductMode','FullPrecision',...
	     'SumMode','FullPrecision');
end
