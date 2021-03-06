from pytest import raises
from phypno.utils import create_data

def test_import():
    import phypno
    print(phypno)

def test_simulate_01():
    data = create_data()
    assert data.data.dtype == 'O'
    assert data.data.shape == (1,)  # one trial
    assert data.data[0].shape[0] == len(data.axis['chan'][0])
    assert data.data[0].shape[1] == len(data.axis['time'][0])

def test_simulate_02():
    with raises(ValueError):
        create_data(datatype='xxx')

def test_simulate_03():
    N_TRIAL = 10
    data = create_data(n_trial=N_TRIAL)
    assert data.data.shape[0] == N_TRIAL


def test_simulate_04():
    data = create_data(datatype='ChanFreq')
    assert data.data[0].shape[0] == len(data.axis['chan'][0])
    assert data.data[0].shape[1] == len(data.axis['freq'][0])


def test_simulate_05():
    data = create_data(datatype='ChanTimeFreq')
    assert data.data[0].shape[0] == len(data.axis['chan'][0])
    assert data.data[0].shape[1] == len(data.axis['time'][0])
    assert data.data[0].shape[2] == len(data.axis['freq'][0])


def test_simulate_06():
    TIME_LIMITS = (0, 10)
    data = create_data(time=TIME_LIMITS)
    assert data.axis['time'][0][0] == TIME_LIMITS[0]
    assert data.axis['time'][0][-1] < TIME_LIMITS[1]


def test_simulate_07():
    FREQ_LIMITS = (0, 10)
    data = create_data(datatype='ChanFreq', freq=FREQ_LIMITS)
    assert data.axis['freq'][0][0] == FREQ_LIMITS[0]
    assert data.axis['freq'][0][-1] < FREQ_LIMITS[1]
