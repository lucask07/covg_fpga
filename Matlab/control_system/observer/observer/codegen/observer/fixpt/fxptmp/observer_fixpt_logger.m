% loggingMode - mode of operation : either read or log
%#codegen
%#internal
function loggedData = observer_fixpt_logger(varargin)
    coder.inline( 'never' );
    coder.extrinsic( 'MException', 'throw' );
    persistent iterCount
    if isempty( iterCount )
        iterCount = 0;
    end
    if nargin>0
        % Log the data.
        y1_TB_logger( varargin{ 1 } );
        y2_TB_logger( varargin{ 2 } );
        u_TB_logger( varargin{ 3 } );
        L_TB_logger( varargin{ 4 } );
        A_TB_logger( varargin{ 5 } );
        B_TB_logger( varargin{ 6 } );
        out_TB_logger( varargin{ 7 } );
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
        loggedData.inputs.y1 = y1_TB_logger();
        loggedData.inputs.y2 = y2_TB_logger();
        loggedData.inputs.u = u_TB_logger();
        loggedData.inputs.L = L_TB_logger();
        loggedData.inputs.A = A_TB_logger();
        loggedData.inputs.B = B_TB_logger();
        loggedData.outputs.out = out_TB_logger();
        loggedData.iterCount = iterCount;
    end
end
function out = y1_TB_logger(v)
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
function out = y2_TB_logger(v)
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
function out = u_TB_logger(v)
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
function out = L_TB_logger(v)
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
function out = A_TB_logger(v)
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
function out = B_TB_logger(v)
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
function out = out_TB_logger(v)
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
