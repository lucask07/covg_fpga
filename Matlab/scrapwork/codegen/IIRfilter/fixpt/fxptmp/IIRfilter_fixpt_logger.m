% loggingMode - mode of operation : either read or log
%#codegen
%#internal
function loggedData = IIRfilter_fixpt_logger(varargin)
    coder.inline( 'never' );
    coder.extrinsic( 'MException', 'throw' );
    persistent iterCount
    if isempty( iterCount )
        iterCount = 0;
    end
    if nargin>0
        % Log the data.
        x_TB_logger( varargin{ 1 } );
        y_TB_logger( varargin{ 2 } );
        iterCount = iterCount + 1;
        loggedData = [  ];
        if iterCount>=Inf
            throw( MException( 'Coder:FXPCONV:MATLABSimBailOut', 'Return early for input computation' ) );
        end
        return
    else
        % Fetch the data.
        % make sure the 'log setup' has been performed
        assert( ~isempty( iterCount ) );
        loggedData.inputs.x = x_TB_logger();
        loggedData.outputs.y = y_TB_logger();
        loggedData.iterCount = iterCount;
    end
end
function out = x_TB_logger(v)
    coder.inline( 'never' );
    persistent p
    coder.varsize( 'p' );
    if nargin==1
        if isempty( p )
            p = [  ];
        end
        if size( v, 1 )>1
            p = [ p; loggableValue( v ) ];
        else
            p = [ p, loggableValue( v ) ];
        end
    else
        assert( ~isempty( p ) );
        out = p;
        p = [  ];
    end
end
function out = y_TB_logger(v)
    coder.inline( 'never' );
    persistent p
    coder.varsize( 'p' );
    if nargin==1
        if isempty( p )
            p = [  ];
        end
        if size( v, 1 )>1
            p = [ p; loggableValue( v ) ];
        else
            p = [ p, loggableValue( v ) ];
        end
    else
        assert( ~isempty( p ) );
        out = p;
        p = [  ];
    end
end
function out = loggableValue(in)
    coder.inline( 'always' );
    if coder.isenum( in )
        out = double( in );
    else
        out = in;
    end
end
