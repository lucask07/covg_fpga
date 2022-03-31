% loggingMode - mode of operation : either read or log
%#codegen
%#internal
function loggedData = sumGain_fixpt_logger(varargin)
    coder.inline( 'never' );
    coder.extrinsic( 'MException', 'throw' );
    persistent iterCount
    if isempty( iterCount )
        iterCount = 0;
    end
    if nargin>0
        % Log the data.
        in1_TB_logger( varargin{ 1 } );
        in2_TB_logger( varargin{ 2 } );
        in3_TB_logger( varargin{ 3 } );
        g1_TB_logger( varargin{ 4 } );
        g2_TB_logger( varargin{ 5 } );
        g3_TB_logger( varargin{ 6 } );
        scaleVal_TB_logger( varargin{ 7 } );
        y_TB_logger( varargin{ 8 } );
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
        loggedData.inputs.in1 = in1_TB_logger();
        loggedData.inputs.in2 = in2_TB_logger();
        loggedData.inputs.in3 = in3_TB_logger();
        loggedData.inputs.g1 = g1_TB_logger();
        loggedData.inputs.g2 = g2_TB_logger();
        loggedData.inputs.g3 = g3_TB_logger();
        loggedData.inputs.scaleVal = scaleVal_TB_logger();
        loggedData.outputs.y = y_TB_logger();
        loggedData.iterCount = iterCount;
    end
end
function out = in1_TB_logger(v)
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
function out = in2_TB_logger(v)
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
function out = in3_TB_logger(v)
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
function out = g1_TB_logger(v)
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
function out = g2_TB_logger(v)
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
function out = g3_TB_logger(v)
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
function out = scaleVal_TB_logger(v)
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
